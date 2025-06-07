# Agregar estas nuevas URLs a tu urls.py existente

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tramites.views import (
    inicio, ver_tramites, ver_detalle_tramite, login_view, logout_view,
    get_users_api, create_user_api, update_user_api, delete_user_api,
    create_tramite_api, update_tramite_api, delete_tramite_api,
    # NUEVAS IMPORTACIONES PARA DETALLE:
    get_tramite_detail_api, update_tramite_detail_api, update_modalidad_api,
    update_requisito_api, update_costo_api, update_opcion_pago_api,
    update_fundamento_juridico_api, update_informacion_adicional_api,
    update_oficina_atencion_api, protesta_view,
    # NUEVA IMPORTACIÓN PARA BÚSQUEDA:
    buscar_api,
    # NUEVAS IMPORTACIONES PARA PROTESTAS:
    get_protestas_api, update_protesta_status_api, generar_protesta_pdf,
    get_grupos_api, cambiar_grupo_usuario_api,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name='REMTyS'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('tramites/<int:clasificacion_id>/', ver_tramites, name='ver_tramites'),
    path('tramite/<int:tramite_id>/', ver_detalle_tramite, name='ver_detalle_tramite'),
    
    # API para búsqueda
    path('api/buscar/', buscar_api, name='buscar_api'),
    
    # APIs para el panel de administración de usuarios
    path('api/users/', get_users_api, name='get_users_api'),
    path('api/users/create/', create_user_api, name='create_user_api'),
    path('api/users/update/', update_user_api, name='update_user_api'),
    path('api/users/delete/', delete_user_api, name='delete_user_api'),
    
    # APIs para trámites básicos
    path('api/tramites/create/', create_tramite_api, name='create_tramite_api'),
    path('api/tramites/update/', update_tramite_api, name='update_tramite_api'),
    path('api/tramites/delete/', delete_tramite_api, name='delete_tramite_api'),
    
    # APIs PARA DETALLE DE TRÁMITES:
    path('api/tramite/<int:tramite_id>/detail/', get_tramite_detail_api, name='get_tramite_detail_api'),
    path('api/tramite/detail/update/', update_tramite_detail_api, name='update_tramite_detail_api'),
    path('api/modalidad/update/', update_modalidad_api, name='update_modalidad_api'),
    path('api/requisito/update/', update_requisito_api, name='update_requisito_api'),
    path('api/costo/update/', update_costo_api, name='update_costo_api'),
    path('api/opcion-pago/update/', update_opcion_pago_api, name='update_opcion_pago_api'),
    path('api/fundamento-juridico/update/', update_fundamento_juridico_api, name='update_fundamento_juridico_api'),
    path('api/informacion-adicional/update/', update_informacion_adicional_api, name='update_informacion_adicional_api'),
    path('api/oficina-atencion/update/', update_oficina_atencion_api, name='update_oficina_atencion_api'),

    # URL PARA PROTESTA CIUDADANA
    path('protesta/', protesta_view, name='protesta'),
    
    # NUEVAS APIs PARA PANEL DE PROTESTAS:
    path('api/protestas/', get_protestas_api, name='get_protestas_api'),
    path('api/protesta/status/update/', update_protesta_status_api, name='update_protesta_status_api'),
    path('api/protesta/<int:protesta_id>/pdf/', generar_protesta_pdf, name='generar_protesta_pdf'),
    
    # NUEVAS APIs PARA GRUPOS DE USUARIOS:
    
    path('api/grupos/', get_grupos_api, name='get_grupos_api'),
    path('api/cambiar-grupo/', cambiar_grupo_usuario_api, name='cambiar_grupo_usuario_api'),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Corregir esta línea - convertir Path a string
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=str(settings.STATICFILES_DIRS[0]))