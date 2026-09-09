# Generated migration for AI ProjectsHub

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('subject', models.CharField(blank=True, max_length=300)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('new', 'New'), ('read', 'Read'), ('replied', 'Replied'), ('archived', 'Archived')], default='new', max_length=20)),
                ('admin_notes', models.TextField(blank=True, help_text='Internal notes (not visible to user)')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Contact Message',
                'verbose_name_plural': 'Contact Messages',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PricingPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('icon_type', models.CharField(choices=[('basic', 'Basic (People)'), ('pro', 'Pro (Briefcase)'), ('enterprise', 'Enterprise (Home)'), ('custom', 'Custom')], default='basic', max_length=20)),
                ('description', models.CharField(max_length=300)),
                ('monthly_price', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('yearly_price', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('monthly_original', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8)),
                ('yearly_original', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=8)),
                ('is_featured', models.BooleanField(default=False, help_text="Show 'Popular' badge")),
                ('is_free', models.BooleanField(default=False, help_text="Display price as 'Free'")),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('cta_label', models.CharField(default='Get Started', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Pricing Plan',
                'verbose_name_plural': 'Pricing Plans',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('detailed_description', models.TextField(blank=True, help_text='Detailed description for the project detail page')),
                ('image', models.ImageField(blank=True, null=True, upload_to='projects/')),
                ('detail_images', models.JSONField(blank=True, help_text="List of additional images [{'url': 'path/to/image.jpg', 'alt': 'Alt text'}]", null=True)),
                ('image_url', models.URLField(blank=True, help_text='External image URL (used if no uploaded image)')),
                ('tags', models.CharField(help_text='Comma-separated tags e.g. PyTorch, FastAPI, AWS', max_length=300)),
                ('category', models.CharField(choices=[('ml', 'Machine Learning'), ('backend', 'Backend'), ('data', 'Data'), ('cloud', 'Cloud')], default='ml', max_length=50)),
                ('project_url', models.URLField(blank=True, help_text='Link to live project or case study')),
                ('youtube_url', models.URLField(blank=True, help_text='YouTube demo URL')),
                ('download_file', models.FileField(blank=True, help_text='Downloadable file for this project', null=True, upload_to='project_files/')),
                ('show_on_index', models.BooleanField(default=False, help_text='Show this project on the homepage projects section')),
                ('is_active', models.BooleanField(default=True, help_text='Show on projects page')),
                ('order', models.PositiveIntegerField(default=0, help_text='Display order (lower = first)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectGateLead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('college_or_org', models.CharField(max_length=300)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Project Gate Lead',
                'verbose_name_plural': 'Project Gate Leads',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WorkshopCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=300)),
                ('description', models.TextField()),
                ('date', models.CharField(help_text='e.g. May 10 – 13, 2026', max_length=100)),
                ('time', models.CharField(help_text='e.g. 10 AM – 5 PM IST', max_length=100)),
                ('seats', models.PositiveIntegerField(default=30)),
                ('mode', models.CharField(default='Online (Live)', max_length=100)),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('price_label', models.CharField(blank=True, help_text='e.g. Free, ₹999', max_length=50)),
                ('enroll_url', models.URLField(blank=True, help_text='Enrollment / registration link')),
                ('is_active', models.BooleanField(default=True)),
                ('is_featured', models.BooleanField(default=False, help_text='Highlight this workshop')),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Workshop Card',
                'verbose_name_plural': 'Workshop Cards',
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WorkshopDay',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day_number', models.PositiveIntegerField()),
                ('title', models.CharField(max_length=200)),
                ('date_label', models.CharField(blank=True, help_text='e.g. Sunday, May 10', max_length=100)),
                ('description', models.TextField()),
                ('outcome', models.CharField(blank=True, help_text='Key outcome for this day', max_length=300)),
                ('workshop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='core.workshopcard')),
            ],
            options={
                'verbose_name': 'Workshop Day',
                'verbose_name_plural': 'Workshop Days',
                'ordering': ['day_number'],
            },
        ),
        migrations.CreateModel(
            name='PricingFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature', models.CharField(max_length=200)),
                ('order', models.PositiveIntegerField(default=0)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='features', to='core.pricingplan')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='project',
            name='pricing_plans',
            field=models.ManyToManyField(blank=True, help_text='Pricing plans associated with this project', related_name='projects', to='core.pricingplan'),
        ),
        migrations.CreateModel(
            name='IdeaSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('project_title', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('budget', models.CharField(blank=True, choices=[('under-5k', 'Under ₹5,000'), ('5k-20k', '₹5,000 – ₹20,000'), ('20k-50k', '₹20,000 – ₹50,000'), ('50k-plus', '₹50,000+'), ('flexible', 'Flexible / Not sure')], max_length=20)),
                ('timeline', models.CharField(blank=True, choices=[('asap', 'ASAP'), ('1-month', 'Within 1 month'), ('3-months', 'Within 3 months'), ('6-months', 'Within 6 months'), ('flexible', 'Flexible')], max_length=20)),
                ('agreed_to_terms', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('new', 'New'), ('reviewing', 'Reviewing'), ('accepted', 'Accepted'), ('declined', 'Declined'), ('completed', 'Completed')], default='new', max_length=20)),
                ('admin_notes', models.TextField(blank=True, help_text='Internal notes (not visible to user)')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Idea Submission',
                'verbose_name_plural': 'Idea Submissions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='WorkshopEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('experience', models.CharField(blank=True, choices=[('beginner', 'Beginner (No prior experience)'), ('basic', 'Basic (Some exposure)'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], max_length=20)),
                ('referral', models.CharField(blank=True, choices=[('social', 'Social Media'), ('friend', 'Friend / Colleague'), ('google', 'Google Search'), ('email', 'Email Newsletter'), ('other', 'Other')], max_length=20)),
                ('message', models.TextField(blank=True, help_text='Optional message from the enrollee')),
                ('agreed_to_terms', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled'), ('attended', 'Attended')], default='pending', max_length=20)),
                ('admin_notes', models.TextField(blank=True, help_text='Internal notes (not visible to user)')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('workshop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='enrollments', to='core.workshopcard')),
            ],
            options={
                'verbose_name': 'Workshop Enrollment',
                'verbose_name_plural': 'Workshop Enrollments',
                'ordering': ['-created_at'],
                'unique_together': {('workshop', 'email')},
            },
        ),
    ]
