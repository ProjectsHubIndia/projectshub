"""
Management command to export all model data to JSON or CSV.
Usage: python manage.py export_data --format=json --output=backup
"""
import csv
import json
from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps


class Command(BaseCommand):
    help = 'Export all model data to JSON or CSV'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='json',
            choices=['json', 'csv'],
            help='Export format: json or csv',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='export_data',
            help='Output file name (without extension)',
        )
        parser.add_argument(
            '--models',
            type=str,
            help='Comma-separated list of models to export (e.g., Project,BlogPost). Default: all core models.',
        )
    
    def handle(self, *args, **options):
        format_type = options['format']
        output_file = f"{options['output']}.{format_type}"
        model_names = options['models'].split(',') if options['models'] else None
        
        # Get models to export from core app
        try:
            app_models = apps.get_app_config('core').get_models()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading core app models: {e}'))
            return
        
        if model_names:
            app_models = [m for m in app_models if m.__name__ in model_names]
        
        if not app_models:
            self.stdout.write(self.style.ERROR('No models found to export'))
            return
        
        self.stdout.write(f'Exporting {len(app_models)} models to {format_type.upper()}...')
        
        if format_type == 'json':
            # JSON export - all models in one file
            all_objects = []
            
            for model in app_models:
                queryset = model.objects.all()
                count = queryset.count()
                if count > 0:
                    all_objects.extend(queryset)
                    self.stdout.write(f'  {model.__name__}: {count} records')
            
            if not all_objects:
                self.stdout.write(self.style.WARNING('No data to export'))
                return
            
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    serializers.serialize('json', all_objects, indent=2, stream=f)
                
                self.stdout.write(self.style.SUCCESS(
                    f'\n✓ Exported {len(all_objects)} records to {output_file}'
                ))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Export failed: {e}'))
        
        else:
            # CSV export - one file per model
            total = 0
            exported_files = []
            
            for model in app_models:
                queryset = model.objects.all()
                if not queryset.exists():
                    continue
                
                model_file = f"{options['output']}_{model.__name__}.csv"
                
                try:
                    with open(model_file, 'w', newline='', encoding='utf-8') as f:
                        fields = [field.name for field in model._meta.fields]
                        writer = csv.DictWriter(f, fieldnames=fields)
                        writer.writeheader()
                        
                        for obj in queryset:
                            row = {}
                            for field_name in fields:
                                val = getattr(obj, field_name)
                                # Handle related objects, files, and None values
                                if val is None:
                                    row[field_name] = ''
                                elif hasattr(val, 'pk'):  # Foreign key
                                    row[field_name] = str(val.pk)
                                elif hasattr(val, 'path'):  # File field
                                    try:
                                        row[field_name] = val.url
                                    except Exception:
                                        row[field_name] = ''
                                else:
                                    row[field_name] = str(val)
                            writer.writerow(row)
                    
                    count = queryset.count()
                    total += count
                    exported_files.append(model_file)
                    self.stdout.write(f'  {model.__name__}: {count} records → {model_file}')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Failed to export {model.__name__}: {e}'))
            
            if exported_files:
                self.stdout.write(self.style.SUCCESS(
                    f'\n✓ Exported {total} total records to {len(exported_files)} CSV files'
                ))
            else:
                self.stdout.write(self.style.WARNING('No data to export'))
