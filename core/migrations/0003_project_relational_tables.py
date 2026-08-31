import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_project_detail_fields'),
    ]

    operations = [
        # ── Remove old JSON fields and M2M from Project ────────────────────────
        migrations.RemoveField(model_name='project', name='detail_images'),
        migrations.RemoveField(model_name='project', name='highlights'),
        migrations.RemoveField(model_name='project', name='diagrams'),
        migrations.RemoveField(model_name='project', name='timeline_phases'),
        migrations.RemoveField(model_name='project', name='price_features'),
        migrations.RemoveField(model_name='project', name='pricing_plans'),

        # ── ProjectImage ───────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='projects/detail/')),
                ('caption', models.CharField(blank=True, max_length=300)),
                ('alt', models.CharField(
                    blank=True, max_length=200,
                    help_text='Alt text (defaults to project title if left blank)'
                )),
                ('order', models.PositiveIntegerField(default=0)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='detail_images', to='core.project'
                )),
            ],
            options={
                'verbose_name': 'Detail Image',
                'verbose_name_plural': 'Detail Images',
                'ordering': ['order'],
            },
        ),

        # ── ProjectHighlight ───────────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectHighlight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('icon', models.CharField(
                    max_length=20,
                    choices=[
                        ('chart', 'Bar Chart'),
                        ('users', 'Users / Team'),
                        ('clock', 'Clock / Time'),
                        ('star', 'Star / Rating'),
                        ('bolt', 'Bolt / Speed'),
                    ],
                    default='chart'
                )),
                ('value', models.CharField(max_length=100, help_text='e.g. 94% or 3 Months')),
                ('label', models.CharField(max_length=100, help_text='e.g. Accuracy or Build Time')),
                ('order', models.PositiveIntegerField(default=0)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='highlights', to='core.project'
                )),
            ],
            options={
                'verbose_name': 'Key Highlight',
                'verbose_name_plural': 'Key Highlights',
                'ordering': ['order'],
            },
        ),

        # ── ProjectDiagram ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectDiagram',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='projects/diagrams/')),
                ('label', models.CharField(
                    blank=True, max_length=100, default='Architecture',
                    help_text='Short badge label, e.g. Architecture, Data Flow'
                )),
                ('title', models.CharField(max_length=200, help_text='Diagram title')),
                ('desc', models.TextField(blank=True, help_text='Short description of the diagram')),
                ('order', models.PositiveIntegerField(default=0)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='diagrams', to='core.project'
                )),
            ],
            options={
                'verbose_name': 'Architecture Diagram',
                'verbose_name_plural': 'Architecture Diagrams',
                'ordering': ['order'],
            },
        ),

        # ── ProjectTimelinePhase ───────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectTimelinePhase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('phase', models.CharField(max_length=100, help_text='Phase label, e.g. Phase 01')),
                ('date', models.CharField(max_length=100, help_text='Date string, e.g. Jan 2025')),
                ('title', models.CharField(max_length=200,
                                           help_text='Phase title, e.g. Research & Planning')),
                ('desc', models.TextField(blank=True, help_text='What happened in this phase')),
                ('order', models.PositiveIntegerField(default=0)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='timeline_phases', to='core.project'
                )),
            ],
            options={
                'verbose_name': 'Timeline Phase',
                'verbose_name_plural': 'Timeline Phases',
                'ordering': ['order'],
            },
        ),

        # ── ProjectFeature ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name='ProjectFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True,
                                           serialize=False, verbose_name='ID')),
                ('text', models.CharField(
                    max_length=300,
                    help_text='e.g. Full source code, Docker setup'
                )),
                ('order', models.PositiveIntegerField(default=0)),
                ('project', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='price_features', to='core.project'
                )),
            ],
            options={
                'verbose_name': "What's Included Feature",
                'verbose_name_plural': "What's Included Features",
                'ordering': ['order'],
            },
        ),
    ]
