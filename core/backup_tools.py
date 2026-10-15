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
import json
import logging
import os
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


# ── Restore ───────────────────────────────────────────────────────────────────

class RestoreError(Exception):
    pass


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
    """Restore a full .zip backup (database.json + media/) made by the download-bundle view.
    Loads the data through restore_backup (snapshot + one transaction), then writes the media
    files back into MEDIA_ROOT. Returns the restore report with a 'media_restored' count."""
    import shutil
    import zipfile
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw_bytes))
    except zipfile.BadZipFile:
        raise RestoreError('The uploaded file is not a valid .zip archive.')
    names = set(zf.namelist())
    data_name = next((n for n in ('database.json', 'initial_data.json') if n in names), None)
    if not data_name:
        raise RestoreError('The .zip has no database.json — is it a full ProjectsHub backup?')

    report = restore_backup(zf.read(data_name))

    media_root = os.path.abspath(settings.MEDIA_ROOT)
    os.makedirs(media_root, exist_ok=True)
    count = 0
    for info in zf.infolist():
        if info.is_dir() or not info.filename.startswith('media/'):
            continue
        rel = info.filename[len('media/'):]
        dest = os.path.abspath(os.path.join(media_root, rel))
        # zip-slip guard: never write outside MEDIA_ROOT
        if not rel or os.path.commonpath([dest, media_root]) != media_root:
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with zf.open(info) as src, open(dest, 'wb') as out:
            shutil.copyfileobj(src, out)
        count += 1
    report['media_restored'] = count
    return report
