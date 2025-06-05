# Agrega esto en tu admin.py para manejar los modelos
from django.contrib import admin
from .models import ClasificacionTramites, Tramite, DetalleTramite, PerfilUsuario
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ProtestaCiudadana

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
    
    
@admin.register(ProtestaCiudadana)
class ProtestaCiudadanaAdmin(admin.ModelAdmin):
    list_display = ('folio', 'get_nombre_completo', 'tramite', 'estatus', 'fecha_creacion')
    list_filter = ('estatus', 'clv_motivo', 'tipo_tramite', 'fecha_creacion')
    search_fields = ('folio', 'nombre', 'apellido_paterno', 'apellido_materno', 'rfc', 'email')
    readonly_fields = ('folio', 'fecha_creacion')
    
    fieldsets = (
        ('Información de Control', {
            'fields': ('folio', 'fecha_creacion', 'estatus')
        }),
        ('Datos del Trámite', {
            'fields': ('tramite', 'area', 'responsable', 'nombre_tramite', 'objeto_protesta')
        }),
        ('Motivo y Procedimiento', {
            'fields': ('clv_motivo', 'tipo_tramite', 'folio_referencia', 'es_presencial', 
                      'lugar_administrativa', 'liga_internet', 'fecha_tramite', 'hora_tramite')
        }),
        ('Información Económica', {
            'fields': ('rfc', 'calificacion_afectacion', 'costo_afectacion', 
                      'costo_letra_afectacion', 'empleos_afectacion')
        }),
        ('Datos Personales', {
            'fields': ('nombre', 'apellido_paterno', 'apellido_materno', 'estado', 'municipio',
                      'calle', 'num_ext', 'num_int', 'colonia', 'codigo_postal', 'referencias_domicilio')
        }),
        ('Contacto', {
            'fields': ('email', 'telefono', 'movil')
        }),
        ('Protesta', {
            'fields': ('descripcion_protesta', 'servidor_publico')
        }),
        ('Archivos', {
            'fields': ('archivo_identificacion', 'archivo_comprobante_dom', 'evidencia')
        }),
    )
    
    def get_nombre_completo(self, obj):
        return obj.get_nombre_completo()
    get_nombre_completo.short_description = 'Nombre Completo'
    
    # Permitir cambiar estatus desde el admin
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Gestión de Protestas Ciudadanas'
        return super().changelist_view(request, extra_context)

    # Acciones personalizadas
    actions = ['marcar_como_en_proceso', 'marcar_como_aprobada', 'marcar_como_negada']
    
    def marcar_como_en_proceso(self, request, queryset):
        updated = queryset.update(estatus='EN_PROCESO')
        self.message_user(request, f'{updated} protestas marcadas como "En Proceso".')
    marcar_como_en_proceso.short_description = 'Marcar como En Proceso'
    
    def marcar_como_aprobada(self, request, queryset):
        updated = queryset.update(estatus='APROBADA')
        self.message_user(request, f'{updated} protestas marcadas como "Aprobada".')
    marcar_como_aprobada.short_description = 'Marcar como Aprobada'
    
    def marcar_como_negada(self, request, queryset):
        updated = queryset.update(estatus='NEGADA')
        self.message_user(request, f'{updated} protestas marcadas como "Negada".')
    marcar_como_negada.short_description = 'Marcar como Negada'