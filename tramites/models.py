from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class ClasificacionTramites(models.Model):
    nombre = models.CharField(max_length=300)
    imagen = models.ImageField(upload_to='imagenes/', null=True, blank=True)

    class Meta:
        db_table = 'clasificacion_tramites'

    def __str__(self):
        return self.nombre


class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clasificacion = models.ForeignKey(ClasificacionTramites, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'


# Signal para crear PerfilUsuario automáticamente cuando se crea un User
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'perfilusuario'):
        instance.perfilusuario.save()


class Tramite(models.Model):
    ESTATUS_CHOICES = (
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    )

    clasificacion = models.ForeignKey(ClasificacionTramites, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField()
    estatus = models.CharField(max_length=10, choices=ESTATUS_CHOICES, default='Activo')

    def __str__(self):
        return self.nombre


class DetalleTramite(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE)
    unidad_administrativa = models.CharField(max_length=300)
    descripcion_servicio = models.TextField()
    nombre_por_normatividad = models.TextField()  # Cambiar a TextField
    clasificacion = models.CharField(max_length=300)
    medios_presentacion = models.CharField(max_length=300)
    documento_obtenido = models.CharField(max_length=300)
    criterios_resolucion = models.TextField()
    requiere_inspeccion = models.BooleanField(default=False)
    objetivo_inspeccion = models.TextField()
    archivo_anexo = models.FileField(upload_to='archivos/', null=True, blank=True)

    def __str__(self):
        return f'Detalle de {self.tramite.nombre}'
    
    # Agregar estos modelos al final de tu models.py existente

class TramiteModalidad(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='modalidades')
    tipo_modalidad = models.CharField(max_length=100)  # 'PERSONAS FÍSICAS', 'PERSONAS JURÍDICO COLECTIVAS', etc.
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_modalidad'

    def __str__(self):
        return f'{self.tramite.nombre} - {self.tipo_modalidad}'


class TramiteRequisito(models.Model):
    TIPO_CHOICES = (
        ('ACCION', 'Acción'),
        ('DOCUMENTO', 'Documento'),
    )
    
    modalidad = models.ForeignKey(TramiteModalidad, on_delete=models.CASCADE, related_name='requisitos')
    descripcion = models.TextField()
    tipo_requisito = models.CharField(max_length=20, choices=TIPO_CHOICES)
    original = models.IntegerField(default=0)
    copia = models.CharField(max_length=50, default='0')  # puede ser número o 'N/A', 'Copia simple'
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_requisito'

    def __str__(self):
        return f'{self.modalidad.tipo_modalidad} - {self.descripcion[:50]}...'


class TramiteCosto(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='costos')
    concepto = models.CharField(max_length=255)
    importe = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    unidad_valor = models.CharField(max_length=50)
    fundamento_juridico = models.TextField()
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_costo'

    def __str__(self):
        return f'{self.tramite.nombre} - {self.concepto}'


class TramiteOpcionPago(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='opciones_pago')
    descripcion = models.CharField(max_length=255)
    observacion = models.TextField(blank=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_opcion_pago'

    def __str__(self):
        return f'{self.tramite.nombre} - {self.descripcion}'


class TramiteFundamentoJuridico(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='fundamentos_juridicos')
    nombre_ley = models.CharField(max_length=500)
    articulos = models.TextField()
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_fundamento_juridico'

    def __str__(self):
        return f'{self.tramite.nombre} - {self.nombre_ley}'


class TramiteInformacionAdicional(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='informacion_adicional')
    pregunta = models.TextField()
    respuesta = models.TextField()
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_informacion_adicional'

    def __str__(self):
        return f'{self.tramite.nombre} - {self.pregunta[:50]}...'


class TramiteArchivoAnexo(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='archivos_anexos')
    descripcion = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='tramites_anexos/')
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_archivo_anexo'

    def __str__(self):
        return f'{self.tramite.nombre} - {self.descripcion}'


class TramiteOficinaAtencion(models.Model):
    tramite = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='oficinas_atencion')
    nombre = models.CharField(max_length=255)
    calle = models.CharField(max_length=255)
    numero_exterior = models.CharField(max_length=20)
    numero_interior = models.CharField(max_length=20, blank=True)
    colonia = models.CharField(max_length=255)
    codigo_postal = models.CharField(max_length=10)
    horario_atencion = models.TextField()
    telefonos = models.CharField(max_length=100)
    celular = models.CharField(max_length=50, blank=True)
    email_responsable = models.EmailField()
    nombre_responsable = models.CharField(max_length=255)
    puesto_responsable = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    longitud = models.DecimalField(max_digits=11, decimal_places=8, blank=True, null=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_oficina_atencion'

    def __str__(self):
        return f'{self.tramite.nombre} - {self.nombre}'


class TramiteRelacionado(models.Model):
    tramite_origen = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='tramites_relacionados')
    tramite_relacionado = models.ForeignKey(Tramite, on_delete=models.CASCADE, related_name='relacionado_con')
    descripcion = models.CharField(max_length=255, blank=True)
    orden = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['orden']
        db_table = 'tramite_relacionado'

    def __str__(self):
        return f'{self.tramite_origen.nombre} -> {self.tramite_relacionado.nombre}'