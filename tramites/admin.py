# Agrega esto en tu admin.py para manejar los modelos
from django.contrib import admin
from .models import ClasificacionTramites, Tramite, DetalleTramite, PerfilUsuario
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

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
     
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)     
    
# Agregar al final de tu admin.py existente
from .models import (
    TramiteModalidad, TramiteRequisito, TramiteCosto, TramiteOpcionPago,
    TramiteFundamentoJuridico, TramiteInformacionAdicional, TramiteArchivoAnexo,
    TramiteOficinaAtencion, TramiteRelacionado
)

class TramiteRequisitoInline(admin.TabularInline):
    model = TramiteRequisito
    extra = 1
    fields = ['descripcion', 'tipo_requisito', 'original', 'copia', 'orden']

@admin.register(TramiteModalidad)
class TramiteModalidadAdmin(admin.ModelAdmin):
    list_display = ['tramite', 'tipo_modalidad', 'orden']
    list_filter = ['tramite', 'tipo_modalidad']
    search_fields = ['tramite__nombre', 'tipo_modalidad']
    inlines = [TramiteRequisitoInline]

@admin.register(TramiteCosto)
class TramiteCostoAdmin(admin.ModelAdmin):
    list_display = ['tramite', 'concepto', 'importe', 'unidad_valor']
    list_filter = ['tramite']
    search_fields = ['tramite__nombre', 'concepto']

@admin.register(TramiteOpcionPago)
class TramiteOpcionPagoAdmin(admin.ModelAdmin):
    list_display = ['tramite', 'descripcion']
    list_filter = ['tramite']
    search_fields = ['tramite__nombre', 'descripcion']

@admin.register(TramiteFundamentoJuridico)
class TramiteFundamentoJuridicoAdmin(admin.ModelAdmin):
    list_display = ['tramite', 'nombre_ley']
    list_filter = ['tramite']
    search_fields = ['tramite__nombre', 'nombre_ley']

@admin.register(TramiteInformacionAdicional)
class TramiteInformacionAdicionalAdmin(admin.ModelAdmin):
    list_display = ['tramite', 'pregunta']
    list_filter = ['tramite']
    search_fields = ['tramite__nombre', 'pregunta']

@admin.register(TramiteArchivoAnexo)
class TramiteArchivoAnexoAdmin(admin.ModelAdmin):
    list_display = ['tramite', 'descripcion']
    list_filter = ['tramite']
    search_fields = ['tramite__nombre', 'descripcion']

@admin.register(TramiteOficinaAtencion)
class TramiteOficinaAtencionAdmin(admin.ModelAdmin):
    list_display = ['tramite', 'nombre', 'telefonos', 'email_responsable']
    list_filter = ['tramite']
    search_fields = ['tramite__nombre', 'nombre', 'email_responsable']

@admin.register(TramiteRelacionado)
class TramiteRelacionadoAdmin(admin.ModelAdmin):
    list_display = ['tramite_origen', 'tramite_relacionado']
    list_filter = ['tramite_origen']
    search_fields = ['tramite_origen__nombre', 'tramite_relacionado__nombre']