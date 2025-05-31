# Agrega esto en tu admin.py para manejar los modelos
from django.contrib import admin
from .models import ClasificacionTramites, Tramite, DetalleTramite, PerfilUsuario

@admin.register(ClasificacionTramites)
class ClasificacionTramitesAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'imagen')
    search_fields = ('nombre',)

@admin.register(Tramite)
class TramiteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'clasificacion', 'estatus')
    list_filter = ('estatus', 'clasificacion')
    search_fields = ('nombre', 'descripcion')
    list_per_page = 20

@admin.register(DetalleTramite)
class DetalleTramiteAdmin(admin.ModelAdmin):
    list_display = ('tramite', 'unidad_administrativa', 'requiere_inspeccion')
    search_fields = ('tramite__nombre', 'unidad_administrativa')
    list_filter = ('requiere_inspeccion',)
    
    
@admin.register(PerfilUsuario)    
class DetallePerfilUsuario(admin.ModelAdmin):
     list_display = ('user', 'clasificacion')
     search_fields = ('user__username', 'clasificacion__nombre')        
     list_filter = ('clasificacion',)