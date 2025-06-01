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
    nombre_por_normatividad = models.CharField(max_length=300)
    clasificacion = models.CharField(max_length=300)
    medios_presentacion = models.CharField(max_length=300)
    documento_obtenido = models.CharField(max_length=300)
    criterios_resolucion = models.TextField()
    requiere_inspeccion = models.BooleanField(default=False)
    objetivo_inspeccion = models.TextField()
    archivo_anexo = models.FileField(upload_to='archivos/', null=True, blank=True)

    def __str__(self):
        return f'Detalle de {self.tramite.nombre}'