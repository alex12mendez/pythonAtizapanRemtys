from django.db import models
from django.contrib.auth.models import User
from django.db import models



class ClasificacionTramites(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='imagenes/', null=True, blank=True)

    class Meta:
        db_table = 'clasificacion_tramites'  # <-- aquí defines el nombre de la tabla manualmente

    def __str__(self):
        return self.nombre



class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clasificacion = models.ForeignKey(ClasificacionTramites, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Perfil de {self.user.username}'


class Tramite(models.Model):
    ESTATUS_CHOICES = (
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
    )

    clasificacion = models.ForeignKey(ClasificacionTramites, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    estatus = models.CharField(max_length=10, choices=ESTATUS_CHOICES, default='Activo')

    def __str__(self):
        return self.nombre

class DetalleTramite(models.Model):
    tramite = models.OneToOneField(Tramite, on_delete=models.CASCADE)
    unidad_administrativa = models.CharField(max_length=255)
    descripcion_servicio = models.TextField()
    nombre_por_normatividad = models.CharField(max_length=255)
    clasificacion = models.CharField(max_length=100)
    medios_presentacion = models.CharField(max_length=255)
    documento_obtenido = models.CharField(max_length=255)
    criterios_resolucion = models.TextField()
    requiere_inspeccion = models.BooleanField(default=False)
    objetivo_inspeccion = models.TextField()
    archivo_anexo = models.FileField(upload_to='archivos/', null=True, blank=True)

    def __str__(self):
        return f'Detalle de {self.tramite.nombre}'
