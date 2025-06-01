from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tramites.views import (
    inicio, ver_tramites, ver_detalle_tramite, login_view, logout_view,
    get_users_api, create_user_api, update_user_api, delete_user_api,
    # AGREGAR ESTAS NUEVAS IMPORTACIONES:
    create_tramite_api, update_tramite_api, delete_tramite_api
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='REMTyS'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('tramites/<int:clasificacion_id>/', ver_tramites, name='ver_tramites'),
    path('tramite/<int:tramite_id>/', ver_detalle_tramite, name='ver_detalle_tramite'),
    
    # APIs para el panel de administración de usuarios
    path('api/users/', get_users_api, name='get_users_api'),
    path('api/users/create/', create_user_api, name='create_user_api'),
    path('api/users/update/', update_user_api, name='update_user_api'),
    path('api/users/delete/', delete_user_api, name='delete_user_api'),
    
    # AGREGAR ESTAS NUEVAS RUTAS PARA TRÁMITES:
    path('api/tramites/create/', create_tramite_api, name='create_tramite_api'),
    path('api/tramites/update/', update_tramite_api, name='update_tramite_api'),
    path('api/tramites/delete/', delete_tramite_api, name='delete_tramite_api'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])