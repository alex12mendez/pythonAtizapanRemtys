
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tramites.views import inicio, ver_tramites, ver_detalle_tramite, login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='REMTyS'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('tramites/<int:clasificacion_id>/', ver_tramites, name='ver_tramites'),
    path('tramite/<int:tramite_id>/', ver_detalle_tramite, name='ver_detalle_tramite'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])