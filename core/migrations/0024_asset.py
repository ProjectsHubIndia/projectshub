# Generated migration for Asset model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_roadmap_plain_projects_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Asset file name or identifier', max_length=255)),
                ('file', models.FileField(blank=True, help_text='Upload asset file', null=True, upload_to='assets/')),
                ('file_url', models.URLField(blank=True, help_text='External CDN or URL for the asset')),
                ('mime_type', models.CharField(blank=True, help_text='MIME type e.g. image/png', max_length=100)),
                ('size_bytes', models.PositiveIntegerField(default=0, help_text='File size in bytes')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, help_text='Usage notes / where it is used')),
                ('is_used', models.BooleanField(default=True, help_text='Whether the asset is currently in use')),
            ],
            options={
                'verbose_name': 'Asset',
                'verbose_name_plural': 'Assets',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
