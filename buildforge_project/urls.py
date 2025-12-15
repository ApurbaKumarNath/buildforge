"""
URL configuration for db_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from builds import views as build_views

from django.conf import settings
from django.conf.urls.static import static

#_________________________________________________________________________________________________________________________ (akn)

urlpatterns = [
    path('admin/', admin.site.urls),

    
    path('accounts/', include(('users.urls', 'users'), namespace='users')), # Any URL starting with 'accounts/' will be handled by our 'users.urls' file.

    path('builds/', include('builds.urls')), # URL starting with 'builds/' will be handled by our builds.urls file.

    path('', build_views.home_view, name='home'), # This is the home page.
]

# necessary configuration to serve media files during development (akn)

# This is for development purposes only. In production, your web server handles this.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#_________________________________________________________________________________________________________________________
