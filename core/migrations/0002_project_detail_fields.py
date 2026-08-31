from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='subtitle',
            field=models.CharField(
                blank=True, max_length=300,
                help_text='Short tagline shown below the title on the detail page'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='year',
            field=models.CharField(blank=True, max_length=10, help_text='Year completed, e.g. 2025'),
        ),
        migrations.AddField(
            model_name='project',
            name='role',
            field=models.CharField(blank=True, max_length=100, help_text='Your role, e.g. ML Engineer'),
        ),
        migrations.AddField(
            model_name='project',
            name='duration',
            field=models.CharField(blank=True, max_length=100, help_text='Build duration, e.g. 3 Months'),
        ),
        migrations.AddField(
            model_name='project',
            name='team_size',
            field=models.CharField(
                blank=True, default='Solo Project', max_length=100,
                help_text='Team size, e.g. Solo Project or 3-person team'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='highlights',
            field=models.JSONField(
                blank=True, null=True,
                help_text='Key metrics: [{"icon":"chart","value":"94%","label":"Accuracy"}, ...]'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='diagrams',
            field=models.JSONField(
                blank=True, null=True,
                help_text='Architecture diagrams: [{"url":"...","label":"Architecture","title":"...","desc":"..."}]'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='timeline_phases',
            field=models.JSONField(
                blank=True, null=True,
                help_text='Build timeline: [{"phase":"Phase 01","date":"Jan 2025","title":"Research","desc":"..."}]'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='github_url',
            field=models.URLField(blank=True, help_text='GitHub repository URL'),
        ),
        migrations.AddField(
            model_name='project',
            name='case_study_url',
            field=models.URLField(blank=True, help_text='Case study PDF or external documentation link'),
        ),
        migrations.AddField(
            model_name='project',
            name='price',
            field=models.DecimalField(
                blank=True, decimal_places=2, default=0, max_digits=8,
                help_text='Project price (0 = free)'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='price_label',
            field=models.CharField(blank=True, max_length=50, help_text='Display label, e.g. ₹2,999 or Free'),
        ),
        migrations.AddField(
            model_name='project',
            name='price_features',
            field=models.JSONField(
                blank=True, null=True,
                help_text="What's included: [\"Full source code\", \"Docker setup\", ...]"
            ),
        ),
    ]
