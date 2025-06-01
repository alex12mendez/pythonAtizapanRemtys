from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import ClasificacionTramites, Tramite, DetalleTramite, PerfilUsuario


def login_view(request):
    """Vista para el login"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('REMTyS')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """Vista para el logout"""
    logout(request)
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('REMTyS')


def inicio(request):
    """Vista principal - Pública para todos, con restricciones solo para usuarios logueados"""
    
    # Si el usuario NO está autenticado, mostrar todas las clasificaciones (público)
    if not request.user.is_authenticated:
        clasificaciones = ClasificacionTramites.objects.all().order_by('id')
    else:
        # Si está autenticado, aplicar restricciones según su perfil
        try:
            perfil = PerfilUsuario.objects.get(user=request.user)
            
            # Si el usuario es admin, puede ver todas las clasificaciones
            if request.user.is_staff or request.user.is_superuser:
                clasificaciones = ClasificacionTramites.objects.all().order_by('id')
            else:
                # Si es usuario normal, solo ve su clasificación asignada
                if perfil.clasificacion:
                    clasificaciones = ClasificacionTramites.objects.filter(id=perfil.clasificacion.id)
                else:
                    clasificaciones = ClasificacionTramites.objects.none()
                    messages.warning(request, 'No tienes asignada ninguna área. Contacta al administrador.')
                    
        except PerfilUsuario.DoesNotExist:
            # Si no tiene perfil, solo los admin pueden ver todo
            if request.user.is_staff or request.user.is_superuser:
                clasificaciones = ClasificacionTramites.objects.all().order_by('id')
            else:
                clasificaciones = ClasificacionTramites.objects.none()
                messages.warning(request, 'No tienes un perfil asignado. Contacta al administrador.')
    
    context = {
        'clasificaciones': clasificaciones,
        'user': request.user,
    }
    return render(request, 'REMTyS.html', context)


def ver_tramites(request, clasificacion_id):
    """Vista de trámites - Pública, con restricciones solo para usuarios logueados"""
    clasificacion = get_object_or_404(ClasificacionTramites, id=clasificacion_id)
    
    # Si el usuario está autenticado, verificar permisos
    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != clasificacion:
                    messages.error(request, 'No tienes permisos para acceder a esta área.')
                    return redirect('REMTyS')
            except PerfilUsuario.DoesNotExist:
                messages.error(request, 'No tienes permisos para acceder a esta área.')
                return redirect('REMTyS')
    
    # Obtener todos los trámites de esta clasificación
    tramites = Tramite.objects.filter(clasificacion=clasificacion).order_by('nombre')
    
    context = {
        'clasificacion': clasificacion,
        'tramites': tramites,
    }
    return render(request, 'ver_tramites.html', context)


def ver_detalle_tramite(request, tramite_id):
    """Vista de detalle de trámite - Pública, con restricciones solo para usuarios logueados"""
    tramite = get_object_or_404(Tramite, id=tramite_id)
    
    # Si el usuario está autenticado, verificar permisos
    if request.user.is_authenticated:
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    messages.error(request, 'No tienes permisos para acceder a este trámite.')
                    return redirect('REMTyS')
            except PerfilUsuario.DoesNotExist:
                messages.error(request, 'No tienes permisos para acceder a este trámite.')
                return redirect('REMTyS')
    
    try:
        detalle = DetalleTramite.objects.get(tramite=tramite)
    except DetalleTramite.DoesNotExist:
        detalle = None
    
    context = {
        'tramite': tramite,
        'detalle': detalle,
    }
    return render(request, 'detalle_tramite.html', context)


# ==================== VISTAS API PARA EL PANEL DE ADMINISTRACIÓN ====================

@csrf_exempt
@require_http_methods(["GET"])
def get_users_api(request):
    """API para obtener todos los usuarios (solo superadmin)"""
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        users_data = []
        users = User.objects.all().order_by('username')
        clasificaciones = ClasificacionTramites.objects.all()
        
        for user in users:
            try:
                perfil = PerfilUsuario.objects.get(user=user)
                clasificacion_id = perfil.clasificacion.id if perfil.clasificacion else None
                clasificacion_nombre = perfil.clasificacion.nombre if perfil.clasificacion else 'Sin área asignada'
            except PerfilUsuario.DoesNotExist:
                clasificacion_id = None
                clasificacion_nombre = 'Sin perfil'
            
            users_data.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'clasificacion_id': clasificacion_id,
                'clasificacion_nombre': clasificacion_nombre,
                'date_joined': user.date_joined.strftime('%d/%m/%Y')
            })
        
        clasificaciones_data = [{'id': c.id, 'nombre': c.nombre} for c in clasificaciones]
        
        return JsonResponse({
            'users': users_data,
            'clasificaciones': clasificaciones_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_user_api(request):
    """API para crear un nuevo usuario (solo superadmin)"""
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not username or not password:
            return JsonResponse({'error': 'Usuario y contraseña son obligatorios'}, status=400)
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'El nombre de usuario ya existe'}, status=400)
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=data.get('is_staff', False)
        )
        
        # Asignar clasificación si se proporciona
        clasificacion_id = data.get('clasificacion_id')
        if clasificacion_id:
            try:
                clasificacion = ClasificacionTramites.objects.get(id=clasificacion_id)
                perfil = PerfilUsuario.objects.get(user=user)
                perfil.clasificacion = clasificacion
                perfil.save()
            except ClasificacionTramites.DoesNotExist:
                pass
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'user_id': user.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_user_api(request):
    """API para actualizar un usuario (solo superadmin)"""
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'ID de usuario requerido'}, status=400)
        
        user = get_object_or_404(User, id=user_id)
        
        # Actualizar campos del usuario
        user.username = data.get('username', user.username).strip()
        user.email = data.get('email', user.email).strip()
        user.first_name = data.get('first_name', user.first_name).strip()
        user.last_name = data.get('last_name', user.last_name).strip()
        user.is_active = data.get('is_active', user.is_active)
        user.is_staff = data.get('is_staff', user.is_staff)
        
        # Cambiar contraseña si se proporciona
        new_password = data.get('new_password', '').strip()
        if new_password:
            user.set_password(new_password)
        
        user.save()
        
        # Actualizar clasificación
        clasificacion_id = data.get('clasificacion_id')
        try:
            perfil = PerfilUsuario.objects.get(user=user)
            if clasificacion_id:
                clasificacion = ClasificacionTramites.objects.get(id=clasificacion_id)
                perfil.clasificacion = clasificacion
            else:
                perfil.clasificacion = None
            perfil.save()
        except (PerfilUsuario.DoesNotExist, ClasificacionTramites.DoesNotExist):
            pass
        
        return JsonResponse({
            'success': True,
            'message': 'Usuario actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_user_api(request):
    """API para eliminar un usuario (solo superadmin)"""
    if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'ID de usuario requerido'}, status=400)
        
        # No permitir que se elimine a sí mismo
        if user_id == request.user.id:
            return JsonResponse({'error': 'No puedes eliminarte a ti mismo'}, status=400)
        
        user = get_object_or_404(User, id=user_id)
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {username} eliminado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)