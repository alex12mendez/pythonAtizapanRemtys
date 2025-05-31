from django.shortcuts import render, get_object_or_404
from .models import ClasificacionTramites, Tramite, DetalleTramite, PerfilUsuario



    
def inicio(request):
    # Obtener todas las clasificaciones de la base de datos
    clasificaciones = ClasificacionTramites.objects.all().order_by('id')
    
    context = {
        'clasificaciones': clasificaciones
    }
    return render(request, 'REMTyS.html', context)

def ver_tramites(request, clasificacion_id):
    clasificacion = get_object_or_404(ClasificacionTramites, id=clasificacion_id)
    
    # Obtener todos los trámites de esta clasificación
    tramites = Tramite.objects.filter(clasificacion=clasificacion).order_by('nombre')
    
    context = {
        'clasificacion': clasificacion,
        'tramites': tramites,
    }
    return render(request, 'ver_tramites.html', context)

def ver_detalle_tramite(request, tramite_id):
    tramite = get_object_or_404(Tramite, id=tramite_id)
    
    try:
        detalle = DetalleTramite.objects.get(tramite=tramite)
    except DetalleTramite.DoesNotExist:
        detalle = None
    
    context = {
        'tramite': tramite,
        'detalle': detalle,
    }
    return render(request, 'detalle_tramite.html', context)