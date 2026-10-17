"""
core/backup_tools.py — database maintenance helpers used by the admin Backup page.

* pending_migrations() / apply_migrations(): detect and apply schema updates from the admin
  (so a missing `manage.py migrate` never leaves features silently broken).
* dump_data(): dumpdata that skips models whose tables don't exist yet.
* restore_backup(): loaddata that tolerates backups taken from another copy of the site
  (e.g. production → local) where the same record has a different id, takes a safety
  snapshot first, runs in one transaction and resets Postgres sequences afterwards.
"""
import io
import hashlib
import json
import logging
import os
import posixpath
import shutil
import stat
import tempfile
from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.core.management import call_command
from django.db import connection, models, transaction

logger = logging.getLogger(__name__)

PENDING_CACHE_KEY = 'ph_pending_migrations'
BACKUP_DIR_NAME = 'backups'
MAX_BUNDLE_FILES = 100000
MAX_BUNDLE_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024


# ── Migrations ────────────────────────────────────────────────────────────────

def pending_migrations(use_cache=True):
    """List of 'app.migration' names that exist in code but are not applied to the database."""
    if use_cache:
        cached = cache.get(PENDING_CACHE_KEY)
        if cached is not None:
            return cached
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(targets)
        pending = [f"{m.app_label}.{m.name}" for m, backwards in plan if not backwards]
    except Exception:
        logger.exception('Could not compute the migration plan')
        pending = []
    cache.set(PENDING_CACHE_KEY, pending, 60)
    return pending


def apply_migrations():
    """Run `migrate` and return its output. Raises on failure."""
    out = io.StringIO()
    call_command('migrate', interactive=False, verbosity=1, stdout=out, stderr=out)
    cache.delete(PENDING_CACHE_KEY)
    return out.getvalue()


# ── Dump ──────────────────────────────────────────────────────────────────────

def _existing_tables():
    with connection.cursor() as cursor:
        return set(connection.introspection.table_names(cursor))


def _models_for_labels(labels):
    result = []
    for label in labels:
        if '.' in label:
            app_label, model_name = label.split('.', 1)
            result.append(apps.get_model(app_label, model_name))
        else:
            result.extend(apps.get_app_config(label).get_models())
    return result


# Models that must never be written into the shipped seed (initial_data.json):
# login credentials/hashes and personal data left by visitors. A fresh deploy
# creates its admin via `seed_admin`; these belong only in private backups.
SEED_EXCLUDE_MODELS = [
    'auth.User',
    'core.ChatbotConversation', 'core.ChatbotMessage', 'core.ChatAgentStatus',
    'core.ContactInquiry', 'core.ContactMessage',
    'core.IdeaSubmission', 'core.WorkshopEnrollment', 'core.ProjectGateLead',
]


def dump_data(labels, exclude=None):
    """dumpdata for the given labels, skipping models whose tables are missing
    (and any in `exclude`). Returns (json_text, skipped_model_labels)."""
    tables = _existing_tables()
    skipped = [m._meta.label for m in _models_for_labels(labels) if m._meta.db_table not in tables]
    skipped += list(exclude or [])
    buf = io.StringIO()
    call_command('dumpdata', *labels, exclude=skipped, natural_foreign=True, natural_primary=True,
                 indent=2, stdout=buf)
    return buf.getvalue(), skipped


def backups_dir():
    path = os.path.join(settings.BASE_DIR, BACKUP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def snapshot(reason='pre-restore'):
    """Save a full JSON snapshot of the current data (not web-accessible). Returns the file path."""
    text, _ = dump_data(['core', 'auth.user'])
    name = f"{reason}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    path = os.path.join(backups_dir(), name)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)
    return path


def snapshot_db_file(reason='pre-update'):
    """Copy the SQLite database file (works even when models and tables are out of sync).
    Returns the path, or None for non-file databases."""
    import shutil
    db = settings.DATABASES['default']
    if 'sqlite3' not in db.get('ENGINE', ''):
        return None
    src = str(db.get('NAME', ''))
    if not os.path.isfile(src):
        return None
    dest = os.path.join(backups_dir(), f"{reason}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.sqlite3")
    shutil.copy2(src, dest)
    return dest


def create_sqlite_snapshot(path):
    """Write a transaction-consistent copy of the active SQLite database to path."""
    if connection.vendor != 'sqlite':
        return False
    connection.ensure_connection()
    if connection.connection is None:
        raise RuntimeError('The SQLite database connection is not available.')
    import sqlite3
    target = sqlite3.connect(path)
    try:
        connection.connection.backup(target)
    finally:
        target.close()
    return True


# ── Restore ───────────────────────────────────────────────────────────────────

class RestoreError(Exception):
    pass


def _zip_member_sha256(zf, info):
    digest = hashlib.sha256()
    size = 0
    with zf.open(info) as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def _parse(raw_bytes):
    try:
        data = json.loads(raw_bytes.decode('utf-8-sig'))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RestoreError(f'The file is not valid JSON ({exc}).')
    if not isinstance(data, list) or not all(isinstance(o, dict) and 'model' in o and 'fields' in o for o in data):
        raise RestoreError('This does not look like a ProjectsHub backup (expected a Django fixture list).')
    return data


def _unique_fields(model):
    return [f for f in model._meta.concrete_fields
            if f.unique and not f.primary_key and not isinstance(f, (models.AutoField, models.BigAutoField))]


def prepare_fixture(objects):
    """
    Make a fixture safe to load into *this* database:
      - drop objects for unknown models or missing tables (reported)
      - when a record with the same unique value (slug, path, …) already exists under a
        different id, load the backup copy onto the existing id and rewrite references to it
    Returns (objects, report).
    """
    tables = _existing_tables()
    report = {'skipped_models': {}, 'remapped': [], 'replaced': [], 'total': 0}
    kept = []
    for obj in objects:
        try:
            model = apps.get_model(obj['model'])
        except (LookupError, ValueError):
            report['skipped_models'][obj['model']] = report['skipped_models'].get(obj['model'], 0) + 1
            continue
        if model._meta.db_table not in tables:
            report['skipped_models'][obj['model']] = report['skipped_models'].get(obj['model'], 0) + 1
            continue
        kept.append(obj)

    # Fill automatic timestamps that hand-made or older backups may leave out.
    from django.utils import timezone as _tz
    now_iso = _tz.now().isoformat()
    for obj in kept:
        model = apps.get_model(obj['model'])
        for field in model._meta.concrete_fields:
            if getattr(field, 'auto_now', False) or getattr(field, 'auto_now_add', False):
                if obj['fields'].get(field.name) in (None, ''):
                    obj['fields'][field.name] = now_iso if isinstance(field, models.DateTimeField) else now_iso[:10]

    # Which pks does the backup itself use, per model?
    incoming_pks = {}
    for obj in kept:
        if obj.get('pk') is not None:
            incoming_pks.setdefault(obj['model'].lower(), set()).add(obj['pk'])

    remap = {}          # (model_label_lower, old_pk) -> new_pk
    to_delete = []      # (model, pk) existing rows that must make way
    for obj in kept:
        pk = obj.get('pk')
        if pk is None:
            continue    # natural-key objects (e.g. auth.user) are matched by loaddata itself
        model = apps.get_model(obj['model'])
        label = obj['model'].lower()
        for field in _unique_fields(model):
            if field.attname not in obj['fields'] and field.name not in obj['fields']:
                continue
            value = obj['fields'].get(field.name, obj['fields'].get(field.attname))
            if value in (None, ''):
                continue
            existing = model._default_manager.filter(**{field.name: value}).exclude(pk=pk).values_list('pk', flat=True).first()
            if existing is None:
                continue
            if existing not in incoming_pks.get(label, set()):
                remap[(label, pk)] = existing
                incoming_pks[label].discard(pk)
                incoming_pks[label].add(existing)
                obj['pk'] = existing
                report['remapped'].append(f"{model._meta.verbose_name} “{value}”: id {pk} → {existing}")
            else:
                # The backup also contains a different record with that id; free the value instead.
                to_delete.append((model, existing))
                report['replaced'].append(f"{model._meta.verbose_name} “{value}” (old id {existing})")
            break

    # Rewrite foreign keys / many-to-many references that pointed at remapped ids.
    if remap:
        for obj in kept:
            model = apps.get_model(obj['model'])
            for field in model._meta.get_fields():
                if not getattr(field, 'concrete', False) and not field.many_to_many:
                    continue
                rel = getattr(field, 'related_model', None)
                if rel is None or not (field.many_to_one or field.one_to_one or field.many_to_many):
                    continue
                rel_label = rel._meta.label_lower
                val = obj['fields'].get(field.name)
                if field.many_to_many and isinstance(val, list):
                    obj['fields'][field.name] = [remap.get((rel_label, v), v) if not isinstance(v, list) else v for v in val]
                elif isinstance(val, int):
                    obj['fields'][field.name] = remap.get((rel_label, val), val)

    report['total'] = len(kept)
    return kept, report, to_delete


def _reset_sequences(model_list):
    if connection.vendor != 'postgresql':
        return
    from django.core.management.color import no_style
    sql = connection.ops.sequence_reset_sql(no_style(), model_list)
    with connection.cursor() as cursor:
        for statement in sql:
            cursor.execute(statement)


def restore_backup(raw_bytes):
    """Validate, snapshot, then load a backup. Returns a report dict. Raises RestoreError."""
    objects = _parse(raw_bytes)
    if pending_migrations(use_cache=False):
        raise RestoreError('The database needs an update before restoring. Click “Apply database update” first.')
    snapshot_path = snapshot('pre-restore')
    with transaction.atomic():
        objects, report, to_delete = prepare_fixture(objects)
        if not objects:
            raise RestoreError('Nothing to restore: the backup contains no records for this site.')
        for model, pk in to_delete:
            model._default_manager.filter(pk=pk).delete()
        fd, tmp_path = tempfile.mkstemp(suffix='.json')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                json.dump(objects, fh)
            out = io.StringIO()
            call_command('loaddata', tmp_path, stdout=out)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        _reset_sequences({apps.get_model(o['model']) for o in objects})
    cache.clear()
    report['snapshot'] = snapshot_path
    return report


def restore_bundle(raw_bytes):
    """Validate a full ZIP, stage media, then restore its portable database and files."""
    import zipfile
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw_bytes))
    except zipfile.BadZipFile:
        raise RestoreError('The uploaded file is not a valid .zip archive.')
    with zf:
        infos = zf.infolist()
        if len(infos) > MAX_BUNDLE_FILES:
            raise RestoreError('The archive contains too many files.')
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise RestoreError('The archive contains duplicate file paths.')
        if sum(info.file_size for info in infos) > MAX_BUNDLE_UNCOMPRESSED_BYTES:
            raise RestoreError('The archive expands beyond the 2 GB restore limit.')
        if zf.testzip() is not None:
            raise RestoreError('The archive is corrupt: a file failed its CRC check.')

        media_infos = []
        for info in infos:
            if info.is_dir() or not info.filename.startswith('media/'):
                continue
            relative = info.filename[len('media/'):]
            normalized = posixpath.normpath(relative)
            file_type = stat.S_IFMT(info.external_attr >> 16)
            if (
                not relative or normalized != relative or normalized.startswith('../')
                or normalized == '..' or '\\' in relative or ':' in relative
                or relative.startswith('/') or file_type == stat.S_IFLNK
            ):
                raise RestoreError(f'The archive contains an unsafe media path: {info.filename!r}.')
            media_infos.append((info, relative))

        data_name = next((n for n in ('database.json', 'initial_data.json') if n in names), None)
        if not data_name:
            raise RestoreError('The .zip has no database.json — is it a full ProjectsHub backup?')

        manifest = None
        if 'manifest.json' in names:
            try:
                manifest = json.loads(zf.read('manifest.json').decode('utf-8'))
            except (UnicodeDecodeError, ValueError) as exc:
                raise RestoreError(f'The backup manifest is invalid: {exc}.') from exc
            if (
                not isinstance(manifest, dict)
                or manifest.get('format') != 'projectshub-full-backup'
                or manifest.get('version') != 1
                or not isinstance(manifest.get('files'), dict)
            ):
                raise RestoreError('The backup manifest has an unsupported format.')

        database_bytes = zf.read(data_name)
        objects = _parse(database_bytes)
        if manifest is not None:
            file_entries = {data_name: zf.getinfo(data_name)}
            file_entries.update({f'media/{relative}': info for info, relative in media_infos})
            if 'database.sqlite3' in names:
                file_entries['database.sqlite3'] = zf.getinfo('database.sqlite3')
            for name, info in file_entries.items():
                expected = manifest['files'].get(name)
                actual_size, actual_digest = _zip_member_sha256(zf, info)
                if (
                    not isinstance(expected, dict)
                    or expected.get('size') != actual_size
                    or expected.get('sha256') != actual_digest
                ):
                    raise RestoreError(f'The backup file failed its SHA-256 check: {name}.')
            if set(manifest['files']) != set(file_entries):
                raise RestoreError('The manifest file list does not match the backup contents.')

        media_root = os.path.realpath(settings.MEDIA_ROOT)
        parent = os.path.dirname(media_root)
        os.makedirs(parent, exist_ok=True)
        installed = []
        with tempfile.TemporaryDirectory(prefix='ph-backup-restore-', dir=parent) as staging:
            staged_media = os.path.join(staging, 'media')
            rollback_media = os.path.join(staging, 'previous')
            os.makedirs(staged_media)
            for info, relative in media_infos:
                staged_path = os.path.join(staged_media, *relative.split('/'))
                os.makedirs(os.path.dirname(staged_path), exist_ok=True)
                with zf.open(info) as src, open(staged_path, 'wb') as out:
                    shutil.copyfileobj(src, out)

            try:
                for _info, relative in media_infos:
                    destination = os.path.realpath(os.path.join(media_root, *relative.split('/')))
                    if os.path.commonpath([destination, media_root]) != media_root:
                        raise RestoreError(f'The media destination escapes MEDIA_ROOT: {relative!r}.')
                    staged_path = os.path.join(staged_media, *relative.split('/'))
                    if os.path.lexists(destination):
                        if os.path.islink(destination) or not os.path.isfile(destination):
                            raise RestoreError(f'The media destination is not a regular file: {relative!r}.')
                        backup_path = os.path.join(rollback_media, *relative.split('/'))
                        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                        os.makedirs(os.path.dirname(destination), exist_ok=True)
                        os.replace(destination, backup_path)
                    else:
                        backup_path = None
                        os.makedirs(os.path.dirname(destination), exist_ok=True)
                    installed.append((destination, backup_path))
                    shutil.copy2(staged_path, destination)

                report = restore_backup(database_bytes)
            except Exception:
                for destination, backup_path in reversed(installed):
                    if os.path.lexists(destination):
                        os.remove(destination)
                    if backup_path and os.path.exists(backup_path):
                        os.makedirs(os.path.dirname(destination), exist_ok=True)
                        os.replace(backup_path, destination)
                raise

        report['media_restored'] = len(media_infos)
        report['sqlite_database_included'] = 'database.sqlite3' in names
        report['manifest_verified'] = manifest is not None
        return report
