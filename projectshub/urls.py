from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from core.views import (
    admin_guide_view, toggle_guide_note, admin_assets_view, admin_asset_delete_view,
    admin_backup_view, admin_backup_download_json, admin_backup_download_db,
    admin_backup_sync_initial, admin_backup_restore,
    error_404, error_500
)

from django.shortcuts import render

admin.site.site_header = "AI ProjectsHub Admin"
admin.site.site_title = "AI ProjectsHub"
admin.site.index_title = "Dashboard"

# Seamlessly render custom admin 404 template even in local dev with DEBUG=True
admin.site.catch_all_view = lambda request, url: render(request, 'admin/404.html', status=404)

urlpatterns = [
    path('admin/guide/toggle/<int:note_id>/', toggle_guide_note, name='toggle_guide_note'),
    path('admin/guide/', admin_guide_view, name='admin_guide'),
    path('admin/assets/delete/', admin_asset_delete_view, name='admin_asset_delete'),
    path('admin/assets/', admin_assets_view, name='admin_assets'),
    path('admin/backup/download-json/', admin_backup_download_json, name='admin_backup_download_json'),
    path('admin/backup/download-db/', admin_backup_download_db, name='admin_backup_download_db'),
    path('admin/backup/sync-initial/', admin_backup_sync_initial, name='admin_backup_sync_initial'),
    path('admin/backup/restore/', admin_backup_restore, name='admin_backup_restore'),
    path('admin/backup/', admin_backup_view, name='admin_backup'),
    path('admin/', admin.site.urls),

    # Serve user-uploaded media unconditionally (production host has no
    # separate rule for /media/, so uploads from the admin need this).
    re_path(
        r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'),
        serve,
        {'document_root': settings.MEDIA_ROOT},
    ),

    # Serve static files fallback (ensures Passenger WSGI / cPanel never 404s on static)
    re_path(
        r'^%s(?P<path>.*)$' % settings.STATIC_URL.lstrip('/'),
        serve,
        {'document_root': settings.STATICFILES_DIRS[0]},
    ),

    # Direct preview routes for custom error pages (accessible even during local development with DEBUG=True)
    path('404/', error_404, name='preview_404'),
    path('admin-404/', lambda request: error_404(request), name='preview_admin_404'),
    path('500/', error_500, name='preview_500'),

    path('', include('core.urls')),

    # Catch-all fallback: seamlessly renders custom 404 page even in local dev (DEBUG=True)
    re_path(r'^.*$', error_404, name='catch_all_404'),
]
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
