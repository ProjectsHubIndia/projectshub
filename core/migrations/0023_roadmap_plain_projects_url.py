from django.db import migrations, models

OLD = '/projects/?category=ml'
NEW = '/projects/'


def drop_category_param(apps, schema_editor):
    apps.get_model('core', 'RoadmapResource').objects.filter(url=OLD).update(url=NEW)
    apps.get_model('core', 'RoadmapSettings').objects.filter(cta_url=OLD).update(cta_url=NEW)
    apps.get_model('core', 'RoadmapSettings').objects.filter(projects_url=OLD).update(projects_url=NEW)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_seed_ai_roadmap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roadmapsettings',
            name='cta_url',
            field=models.CharField(default='/projects/', help_text='Where the drawer footer CTA points.', max_length=255),
        ),
        migrations.AlterField(
            model_name='roadmapsettings',
            name='projects_url',
            field=models.CharField(default='/projects/', help_text='Used by auto-generated "Premium" project resources.', max_length=255),
        ),
        migrations.RunPython(drop_category_param, migrations.RunPython.noop),
    ]
