from django.db import migrations

from core.roadmap_seed import import_roadmap, load_seed


def seed(apps, schema_editor):
    Node = apps.get_model('core', 'RoadmapNode')
    # Only seed a fresh install; never clobber a roadmap someone already edited.
    if Node.objects.exists():
        return

    import_roadmap(
        Node,
        apps.get_model('core', 'RoadmapGroup'),
        apps.get_model('core', 'RoadmapTopic'),
        apps.get_model('core', 'RoadmapResource'),
        chapters=load_seed(),
    )
    apps.get_model('core', 'RoadmapSettings').objects.get_or_create(id=1)


def unseed(apps, schema_editor):
    apps.get_model('core', 'RoadmapNode').objects.all().delete()
    apps.get_model('core', 'RoadmapSettings').objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_roadmapgroup_roadmapnode_roadmapsettings_and_more'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
