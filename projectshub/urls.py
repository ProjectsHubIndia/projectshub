from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.views.generic.base import RedirectView
from core.views import (
    admin_guide_view, toggle_guide_note, admin_assets_view, admin_asset_delete_view,
    admin_backup_view, admin_backup_download_json, admin_backup_download_db,
    admin_backup_sync_initial, admin_backup_restore,
    admin_nav_menus_view, admin_plugins_view, admin_settings_view, admin_quick_edit_api,
    error_400, error_404, error_500
)

from django.shortcuts import render

admin.site.site_header = "AI ProjectsHub Admin"
admin.site.site_title = "AI ProjectsHub"
admin.site.index_title = "Dashboard"

# Seamlessly render custom admin 404 template even in local dev with DEBUG=True
admin.site.catch_all_view = lambda request, url: render(request, 'admin/404.html', status=404)

urlpatterns = [
    # Seamless redirect for /admin without trailing slash
    path('admin', RedirectView.as_view(url='/admin/', permanent=True, query_string=True)),
    path('admin/guide/toggle/<int:note_id>/', toggle_guide_note, name='toggle_guide_note'),
    path('admin/guide/', admin_guide_view, name='admin_guide'),
    path('admin/assets/delete/', admin_asset_delete_view, name='admin_asset_delete'),
    path('admin/assets/', admin_assets_view, name='admin_assets'),
    path('admin/appearance/menus/', admin_nav_menus_view, name='admin_nav_menus'),
    path('admin/plugins/', admin_plugins_view, name='admin_plugins'),
    path('admin/settings/', admin_settings_view, name='admin_settings'),
    path('admin/pages/', RedirectView.as_view(url='/admin/core/page/', permanent=False)),
    path('admin/pages/new/', RedirectView.as_view(url='/admin/core/page/add/', permanent=False)),
    path('admin/api/quick-edit/', admin_quick_edit_api, name='admin_quick_edit_api'),
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
    path('400/', error_400, name='preview_400'),
    path('404/', error_404, name='preview_404'),
    path('admin-404/', lambda request: error_404(request), name='preview_admin_404'),
    path('500/', error_500, name='preview_500'),

    path('', include('core.urls')),

    # Catch-all fallback: seamlessly renders custom 404 page even in local dev (DEBUG=True)
    re_path(r'^.*$', error_404, name='catch_all_404'),
]
handler400 = 'core.views.error_400'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
