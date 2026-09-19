# Generated manually for Google Analytics settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_pricingfeature_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='google_analytics_id',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Google Analytics 4 Measurement ID (e.g., G-XXXXXXXXXX) or Tracking ID (UA-XXXXXXXX-X)',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='custom_head_code',
            field=models.TextField(
                blank=True,
                default='',
                help_text='Custom scripts or tags injected directly before </head> (e.g. Google Tag Manager, Search Console meta tag, etc.)',
            ),
        ),
    ]
