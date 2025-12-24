# buildforge_project/urls.py

from django.contrib import admin
from django.urls import path, include
from builds import views as build_views
# Make sure you have these imports for media files
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # The clean, standard way to include app URLs.
    # Django will automatically discover the 'app_name' from each urls.py file.
    path('accounts/', include('users.urls')),
    path('builds/', include('builds.urls')),
    path('catalog/', include('catalog.urls')),

    path('', build_views.home_view, name='home'),
]

# This is for serving user-uploaded images during development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)