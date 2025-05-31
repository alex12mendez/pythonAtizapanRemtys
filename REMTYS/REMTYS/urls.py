"""
URL configuration for REMTYS project.

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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tramites.views import inicio
from tramites.views import inicio, ver_tramites, ver_detalle_tramite

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='REMTyS'),
    path('tramites/<int:clasificacion_id>/', ver_tramites, name='ver_tramites'),
    path('tramite/<int:tramite_id>/', ver_detalle_tramite, name='ver_detalle_tramite'),
    
]



# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])