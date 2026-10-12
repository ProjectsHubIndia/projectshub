"""Seed data loader for the AI Engineer Roadmap.

The roadmap used to live as 13 hardcoded timeline nodes in the template plus a
~79KB `roadmapData` object in static/js/ai_roadmap.js. That content was lifted
into core/fixtures/ai_roadmap_seed.json so it can be managed from the admin.

Both the data migration and the `import_ai_roadmap` management command go
through `import_roadmap()` here, so there is exactly one copy of the logic.
"""
import json
import os

from django.utils.text import slugify

SEED_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'ai_roadmap_seed.json')


def load_seed(path=None):
    """Read the seed fixture and return its `chapters` list."""
    with open(path or SEED_PATH, encoding='utf-8') as fh:
        return json.load(fh)['chapters']


def import_roadmap(Node, Group, Topic, Resource, chapters=None, replace_resources=True):
    """Create or update roadmap rows from the seed data.

    Safe to re-run: chapters match on `number`, sub-sections on
    (chapter, title), topics on `key`. Pass model classes directly, or the
    historical ones from `apps.get_model` inside a migration.

    `replace_resources=False` leaves each topic's existing resource rows alone,
    so a re-import refreshes copy without discarding links added in the admin.

    Returns a dict of counts.
    """
    chapters = chapters if chapters is not None else load_seed()
    counts = {'chapters': 0, 'groups': 0, 'topics': 0, 'resources': 0}

    for chapter in chapters:
        node, _ = Node.objects.update_or_create(
            number=chapter['number'],
            defaults={
                'title': chapter['title'],
                'icon': chapter['icon'],
                'order': chapter['order'],
                'is_active': True,
            },
        )
        # `slug` is populated by Model.save(), which migrations do not call.
        if not node.slug:
            node.slug = slugify(chapter['title']) or 'chapter-{}'.format(node.number)
            node.save(update_fields=['slug'])
        counts['chapters'] += 1

        groups = {}
        for group in chapter['groups']:
            obj, _ = Group.objects.update_or_create(
                node=node, title=group['title'],
                defaults={'order': group['order'], 'is_active': True},
            )
            groups[group['title']] = obj
            counts['groups'] += 1

        for topic in chapter['topics']:
            obj, _ = Topic.objects.update_or_create(
                key=topic['key'],
                defaults={
                    'node': node,
                    'group': groups.get(topic['group']),
                    'label': topic['label'],
                    'title': topic['title'],
                    'description': topic['description'],
                    'image_url': topic['image_url'],
                    'order': topic['order'],
                    'is_active': True,
                },
            )
            counts['topics'] += 1

            if not topic['resources']:
                continue
            if replace_resources:
                Resource.objects.filter(topic=obj).delete()
            elif Resource.objects.filter(topic=obj).exists():
                continue
            Resource.objects.bulk_create([
                Resource(
                    topic=obj,
                    tier=r['tier'],
                    resource_type=r['resource_type'],
                    label=r['label'],
                    title=r['title'],
                    url=r['url'],
                    order=r['order'],
                    is_active=True,
                )
                for r in topic['resources']
            ])
            counts['resources'] += len(topic['resources'])

    return counts
