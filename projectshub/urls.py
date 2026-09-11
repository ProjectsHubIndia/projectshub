from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from core.views import admin_guide_view, toggle_guide_note, admin_assets_view, admin_asset_delete_view

admin.site.site_header = "AI ProjectsHub Admin"
admin.site.site_title = "AI ProjectsHub"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path('admin/guide/toggle/<int:note_id>/', toggle_guide_note, name='toggle_guide_note'),
    path('admin/guide/', admin_guide_view, name='admin_guide'),
    path('admin/assets/delete/', admin_asset_delete_view, name='admin_asset_delete'),
    path('admin/assets/', admin_assets_view, name='admin_assets'),
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

    path('', include('core.urls')),
]
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
