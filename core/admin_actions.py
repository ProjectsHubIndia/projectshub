"""
Additional admin actions for bulk operations and data management.
These actions can be registered with any ModelAdmin.
"""
from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
import csv
import json


def bulk_mark_as_active(modeladmin, request, queryset):
    """Mark selected items as active"""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        f'Successfully marked {updated} item(s) as active.',
        level='SUCCESS'
    )
bulk_mark_as_active.short_description = "✓ Mark selected as active"


def bulk_mark_as_inactive(modeladmin, request, queryset):
    """Mark selected items as inactive"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        f'Successfully marked {updated} item(s) as inactive.',
        level='SUCCESS'
    )
bulk_mark_as_inactive.short_description = "⊗ Mark selected as inactive"


def bulk_publish(modeladmin, request, queryset):
    """Publish selected items"""
    updated = queryset.update(is_published=True)
    modeladmin.message_user(
        request,
        f'Successfully published {updated} item(s).',
        level='SUCCESS'
    )
bulk_publish.short_description = "📢 Publish selected"


def bulk_unpublish(modeladmin, request, queryset):
    """Unpublish selected items"""
    updated = queryset.update(is_published=False)
    modeladmin.message_user(
        request,
        f'Successfully unpublished {updated} item(s).',
        level='SUCCESS'
    )
bulk_unpublish.short_description = "🔒 Unpublish selected"


def bulk_mark_as_featured(modeladmin, request, queryset):
    """Mark selected items as featured"""
    updated = queryset.update(featured=True)
    modeladmin.message_user(
        request,
        f'Successfully marked {updated} item(s) as featured.',
        level='SUCCESS'
    )
bulk_mark_as_featured.short_description = "⭐ Mark as featured"


def bulk_unmark_as_featured(modeladmin, request, queryset):
    """Unmark selected items as featured"""
    updated = queryset.update(featured=False)
    modeladmin.message_user(
        request,
        f'Successfully unmarked {updated} item(s) as featured.',
        level='SUCCESS'
    )
bulk_unmark_as_featured.short_description = "☆ Unmark as featured"


# Lead/Inquiry management actions

def bulk_mark_as_new(modeladmin, request, queryset):
    """Mark selected leads as new"""
    updated = queryset.update(status='new')
    modeladmin.message_user(
        request,
        f'Successfully marked {updated} lead(s) as new.',
        level='SUCCESS'
    )
bulk_mark_as_new.short_description = "🆕 Mark as new"


def bulk_mark_as_contacted(modeladmin, request, queryset):
    """Mark selected leads as contacted"""
    updated = queryset.update(status='contacted')
    modeladmin.message_user(
        request,
        f'Successfully marked {updated} lead(s) as contacted.',
        level='SUCCESS'
    )
bulk_mark_as_contacted.short_description = "📞 Mark as contacted"


def bulk_mark_as_converted(modeladmin, request, queryset):
    """Mark selected leads as converted"""
    updated = queryset.update(status='converted')
    modeladmin.message_user(
        request,
        f'Successfully marked {updated} lead(s) as converted.',
        level='SUCCESS'
    )
bulk_mark_as_converted.short_description = "✅ Mark as converted"


def bulk_mark_as_spam(modeladmin, request, queryset):
    """Mark selected leads as spam"""
    updated = queryset.update(status='spam')
    modeladmin.message_user(
        request,
        f'Successfully marked {updated} lead(s) as spam.',
        level='WARNING'
    )
bulk_mark_as_spam.short_description = "🚫 Mark as spam"


# Export actions

def export_selected_as_json(modeladmin, request, queryset):
    """Export selected items as JSON"""
    model_name = modeladmin.model.__name__
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{model_name.lower()}_export_{timestamp}.json'
    
    # Get field names
    opts = modeladmin.model._meta
    field_names = [f.name for f in opts.fields if not f.many_to_many and not f.one_to_many]
    
    data = []
    for obj in queryset:
        record = {}
        for field in field_names:
            value = getattr(obj, field, None)
            
            # Handle special types
            if hasattr(value, 'isoformat'):  # datetime/date
                value = value.isoformat()
            elif hasattr(value, 'url'):  # File/ImageField
                value = value.url if value else None
            elif hasattr(value, 'pk'):  # Related object
                value = str(value)
            elif value is None:
                value = None
            else:
                value = str(value)
            
            record[field] = value
        data.append(record)
    
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    json.dump(data, response, indent=2, ensure_ascii=False)
    
    modeladmin.message_user(
        request,
        f'Successfully exported {len(data)} record(s) as JSON.',
        level='SUCCESS'
    )
    return response
export_selected_as_json.short_description = "📦 Export selected as JSON"


def export_selected_with_details(modeladmin, request, queryset):
    """Export selected items with all fields to CSV"""
    opts = modeladmin.model._meta
    model_name = opts.model_name
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{model_name}_detailed_export_{timestamp}.csv'
    
    # Get all field names including read-only
    field_names = [f.name for f in opts.get_fields() if not f.many_to_many and not f.one_to_many]
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    writer.writerow(field_names)
    
    for obj in queryset:
        row = []
        for field in field_names:
            try:
                value = getattr(obj, field, '')
                
                # Handle special types
                if hasattr(value, 'isoformat'):  # datetime/date
                    value = value.isoformat()
                elif hasattr(value, 'url'):  # File/ImageField
                    value = value.url if value else ''
                elif hasattr(value, 'pk'):  # Related object
                    value = str(value)
                elif callable(value):
                    value = value()
                
                row.append(str(value) if value is not None else '')
            except Exception as e:
                row.append(f'[Error: {str(e)}]')
        
        writer.writerow(row)
    
    modeladmin.message_user(
        request,
        f'Successfully exported {queryset.count()} record(s) with full details.',
        level='SUCCESS'
    )
    return response
export_selected_with_details.short_description = "📊 Export with full details (CSV)"


# Batch update actions

def bulk_update_order_sequential(modeladmin, request, queryset):
    """Update order field sequentially starting from 1"""
    with transaction.atomic():
        for index, obj in enumerate(queryset.order_by('order'), start=1):
            obj.order = index
            obj.save(update_fields=['order'])
    
    modeladmin.message_user(
        request,
        f'Successfully reordered {queryset.count()} item(s) sequentially.',
        level='SUCCESS'
    )
bulk_update_order_sequential.short_description = "🔢 Reorder sequentially (1, 2, 3...)"


def bulk_reset_order_to_zero(modeladmin, request, queryset):
    """Reset order field to 0 for all selected items"""
    updated = queryset.update(order=0)
    modeladmin.message_user(
        request,
        f'Successfully reset order for {updated} item(s) to 0.',
        level='SUCCESS'
    )
bulk_reset_order_to_zero.short_description = "↻ Reset order to 0"


def bulk_increment_order(modeladmin, request, queryset):
    """Increment order field by 10 for selected items"""
    with transaction.atomic():
        for obj in queryset:
            obj.order = (obj.order or 0) + 10
            obj.save(update_fields=['order'])
    
    modeladmin.message_user(
        request,
        f'Successfully incremented order by 10 for {queryset.count()} item(s).',
        level='SUCCESS'
    )
bulk_increment_order.short_description = "⬆️ Increment order by 10"


# Utility actions

def duplicate_selected_items(modeladmin, request, queryset):
    """Duplicate selected items (copy as drafts if applicable)"""
    model = modeladmin.model
    count = 0
    
    with transaction.atomic():
        for obj in queryset:
            orig_pk = obj.pk
            obj.pk = None
            obj.id = None
            
            # Handle common fields
            if hasattr(obj, 'title'):
                obj.title = f"{obj.title} (Copy)"
            if hasattr(obj, 'name'):
                obj.name = f"{obj.name} (Copy)"
            if hasattr(obj, 'slug'):
                base_slug = f"{obj.slug}-copy"
                new_slug = base_slug
                idx = 1
                while model.objects.filter(slug=new_slug).exists():
                    new_slug = f"{base_slug}-{idx}"
                    idx += 1
                obj.slug = new_slug
            if hasattr(obj, 'is_published'):
                obj.is_published = False
            if hasattr(obj, 'is_active'):
                obj.is_active = False
            
            obj.save()
            count += 1
    
    modeladmin.message_user(
        request,
        f'Successfully duplicated {count} item(s).',
        level='SUCCESS'
    )
duplicate_selected_items.short_description = "📋 Duplicate selected items"


def show_selected_ids(modeladmin, request, queryset):
    """Display IDs of selected items (useful for debugging)"""
    ids = list(queryset.values_list('id', flat=True))
    id_list = ', '.join(str(id) for id in ids)
    
    modeladmin.message_user(
        request,
        f'Selected IDs ({len(ids)}): {id_list}',
        level='INFO'
    )
show_selected_ids.short_description = "🔍 Show selected IDs"


# Common action sets for different model types

CONTENT_ACTIONS = [
    bulk_mark_as_active,
    bulk_mark_as_inactive,
    bulk_publish,
    bulk_unpublish,
    bulk_mark_as_featured,
    bulk_unmark_as_featured,
    export_selected_as_json,
    export_selected_with_details,
    duplicate_selected_items,
    bulk_update_order_sequential,
    bulk_increment_order,
]

LEAD_ACTIONS = [
    bulk_mark_as_new,
    bulk_mark_as_contacted,
    bulk_mark_as_converted,
    bulk_mark_as_spam,
    export_selected_as_json,
    export_selected_with_details,
]

ORDERING_ACTIONS = [
    bulk_update_order_sequential,
    bulk_reset_order_to_zero,
    bulk_increment_order,
]

STANDARD_ACTIONS = [
    export_selected_as_json,
    export_selected_with_details,
    show_selected_ids,
]
