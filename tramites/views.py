# Agregar estos imports al inicio de tu views.py (en la sección de imports existentes)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models  # ← AGREGAR ESTA LÍNEA
from django.core.paginator import Paginator  # ← AGREGAR ESTA LÍNEA
from django.template.loader import get_template  # ← AGREGAR ESTA LÍNEA
import json
import unicodedata
import re
from io import BytesIO  # ← AGREGAR ESTA LÍNEA
import os  # ← AGREGAR ESTA LÍNEA

# Imports para PDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .models import ClasificacionTramites, Tramite, DetalleTramite, PerfilUsuario
from .models import (
    ClasificacionTramites, Tramite, DetalleTramite, PerfilUsuario,
    TramiteModalidad, TramiteRequisito, TramiteCosto, TramiteOpcionPago,
    TramiteFundamentoJuridico, TramiteInformacionAdicional, TramiteArchivoAnexo,
    TramiteOficinaAtencion, TramiteRelacionado, ProtestaCiudadana,
)


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
    
    # Obtener toda la información adicional del trámite
    modalidades = tramite.modalidades.all()
    costos = tramite.costos.all()
    opciones_pago = tramite.opciones_pago.all()
    fundamentos_juridicos = tramite.fundamentos_juridicos.all()
    informacion_adicional = tramite.informacion_adicional.all()
    archivos_anexos = tramite.archivos_anexos.all()
    oficinas_atencion = tramite.oficinas_atencion.all()
    tramites_relacionados = tramite.tramites_relacionados.all()
    
    context = {
        'tramite': tramite,
        'detalle': detalle,
        'modalidades': modalidades,
        'costos': costos,
        'opciones_pago': opciones_pago,
        'fundamentos_juridicos': fundamentos_juridicos,
        'informacion_adicional': informacion_adicional,
        'archivos_anexos': archivos_anexos,
        'oficinas_atencion': oficinas_atencion,
        'tramites_relacionados': tramites_relacionados,
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
    
    
    
    # AGREGAR ESTAS NUEVAS FUNCIONES AL FINAL DE TU views.py EXISTENTE

@csrf_exempt
@require_http_methods(["POST"])
def create_tramite_api(request):
    """API para crear un nuevo trámite"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        clasificacion_id = data.get('clasificacion_id')
        
        if not clasificacion_id:
            return JsonResponse({'error': 'Clasificación requerida'}, status=400)
        
        clasificacion = get_object_or_404(ClasificacionTramites, id=clasificacion_id)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para crear trámites en esta área'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Validar datos requeridos
        nombre = data.get('nombre', '').strip()
        descripcion = data.get('descripcion', '').strip()
        estatus = data.get('estatus', 'Activo')
        
        if not nombre:
            return JsonResponse({'error': 'El nombre es obligatorio'}, status=400)
        
        if not descripcion:
            return JsonResponse({'error': 'La descripción es obligatoria'}, status=400)
        
        # Crear trámite
        tramite = Tramite.objects.create(
            clasificacion=clasificacion,
            nombre=nombre,
            descripcion=descripcion,
            estatus=estatus
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Trámite creado exitosamente',
            'tramite': {
                'id': tramite.id,
                'nombre': tramite.nombre,
                'descripcion': tramite.descripcion,
                'estatus': tramite.estatus
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_tramite_api(request):
    """API para actualizar un trámite"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        tramite_id = data.get('tramite_id')
        
        if not tramite_id:
            return JsonResponse({'error': 'ID de trámite requerido'}, status=400)
        
        tramite = get_object_or_404(Tramite, id=tramite_id)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar campos
        tramite.nombre = data.get('nombre', tramite.nombre).strip()
        tramite.descripcion = data.get('descripcion', tramite.descripcion).strip()
        tramite.estatus = data.get('estatus', tramite.estatus)
        
        if not tramite.nombre:
            return JsonResponse({'error': 'El nombre es obligatorio'}, status=400)
        
        if not tramite.descripcion:
            return JsonResponse({'error': 'La descripción es obligatoria'}, status=400)
        
        tramite.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Trámite actualizado exitosamente',
            'tramite': {
                'id': tramite.id,
                'nombre': tramite.nombre,
                'descripcion': tramite.descripcion,
                'estatus': tramite.estatus
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_tramite_api(request):
    """API para eliminar un trámite"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        tramite_id = data.get('tramite_id')
        
        if not tramite_id:
            return JsonResponse({'error': 'ID de trámite requerido'}, status=400)
        
        tramite = get_object_or_404(Tramite, id=tramite_id)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para eliminar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        nombre_tramite = tramite.nombre
        tramite.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Trámite "{nombre_tramite}" eliminado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
    # AGREGAR ESTAS FUNCIONES AL FINAL DE TU views.py EXISTENTE

@csrf_exempt
@require_http_methods(["GET"])
def get_tramite_detail_api(request, tramite_id):
    """API para obtener todos los detalles de un trámite"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        tramite = get_object_or_404(Tramite, id=tramite_id)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para ver este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Obtener detalle del trámite
        try:
            detalle = DetalleTramite.objects.get(tramite=tramite)
            detalle_data = {
                'unidad_administrativa': detalle.unidad_administrativa,
                'descripcion_servicio': detalle.descripcion_servicio,
                'nombre_por_normatividad': detalle.nombre_por_normatividad,
                'clasificacion': detalle.clasificacion,
                'medios_presentacion': detalle.medios_presentacion,
                'documento_obtenido': detalle.documento_obtenido,
                'criterios_resolucion': detalle.criterios_resolucion,
                'requiere_inspeccion': detalle.requiere_inspeccion,
                'objetivo_inspeccion': detalle.objetivo_inspeccion,
            }
        except DetalleTramite.DoesNotExist:
            detalle_data = None
        
        return JsonResponse({
            'success': True,
            'tramite': {
                'id': tramite.id,
                'nombre': tramite.nombre,
                'descripcion': tramite.descripcion,
                'estatus': tramite.estatus
            },
            'detalle': detalle_data
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_tramite_detail_api(request):
    """API para actualizar los detalles de un trámite"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        tramite_id = data.get('tramite_id')
        
        if not tramite_id:
            return JsonResponse({'error': 'ID de trámite requerido'}, status=400)
        
        tramite = get_object_or_404(Tramite, id=tramite_id)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Obtener o crear DetalleTramite
        detalle, created = DetalleTramite.objects.get_or_create(tramite=tramite)
        
        # Actualizar campos del detalle
        detalle.unidad_administrativa = data.get('unidad_administrativa', detalle.unidad_administrativa)
        detalle.descripcion_servicio = data.get('descripcion_servicio', detalle.descripcion_servicio)
        detalle.nombre_por_normatividad = data.get('nombre_por_normatividad', detalle.nombre_por_normatividad)
        detalle.clasificacion = data.get('clasificacion', detalle.clasificacion)
        detalle.medios_presentacion = data.get('medios_presentacion', detalle.medios_presentacion)
        detalle.documento_obtenido = data.get('documento_obtenido', detalle.documento_obtenido)
        detalle.criterios_resolucion = data.get('criterios_resolucion', detalle.criterios_resolucion)
        detalle.requiere_inspeccion = data.get('requiere_inspeccion', detalle.requiere_inspeccion)
        detalle.objetivo_inspeccion = data.get('objetivo_inspeccion', detalle.objetivo_inspeccion)
        
        detalle.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Detalles del trámite actualizados exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_modalidad_api(request):
    """API para actualizar modalidades y requisitos"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        modalidad_id = data.get('modalidad_id')
        tramite_id = data.get('tramite_id')
        
        if modalidad_id:
            # Actualizar modalidad existente
            modalidad = get_object_or_404(TramiteModalidad, id=modalidad_id)
            tramite = modalidad.tramite
        elif tramite_id:
            # Crear nueva modalidad
            tramite = get_object_or_404(Tramite, id=tramite_id)
            modalidad = TramiteModalidad.objects.create(
                tramite=tramite,
                tipo_modalidad=data.get('tipo_modalidad', ''),
                orden=data.get('orden', 0)
            )
        else:
            return JsonResponse({'error': 'ID de modalidad o trámite requerido'}, status=400)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar modalidad
        if modalidad_id:
            modalidad.tipo_modalidad = data.get('tipo_modalidad', modalidad.tipo_modalidad)
            modalidad.orden = data.get('orden', modalidad.orden)
            modalidad.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Modalidad actualizada exitosamente',
            'modalidad': {
                'id': modalidad.id,
                'tipo_modalidad': modalidad.tipo_modalidad,
                'orden': modalidad.orden
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_requisito_api(request):
    """API para actualizar requisitos"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        requisito_id = data.get('requisito_id')
        modalidad_id = data.get('modalidad_id')
        
        if requisito_id:
            # Actualizar requisito existente
            requisito = get_object_or_404(TramiteRequisito, id=requisito_id)
            modalidad = requisito.modalidad
        elif modalidad_id:
            # Crear nuevo requisito
            modalidad = get_object_or_404(TramiteModalidad, id=modalidad_id)
            requisito = TramiteRequisito.objects.create(
                modalidad=modalidad,
                descripcion=data.get('descripcion', ''),
                tipo_requisito=data.get('tipo_requisito', 'DOCUMENTO'),
                original=data.get('original', 0),
                copia=data.get('copia', '0'),
                orden=data.get('orden', 0)
            )
        else:
            return JsonResponse({'error': 'ID de requisito o modalidad requerido'}, status=400)
        
        # Verificar permisos
        tramite = modalidad.tramite
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar requisito
        if requisito_id:
            requisito.descripcion = data.get('descripcion', requisito.descripcion)
            requisito.tipo_requisito = data.get('tipo_requisito', requisito.tipo_requisito)
            requisito.original = data.get('original', requisito.original)
            requisito.copia = data.get('copia', requisito.copia)
            requisito.orden = data.get('orden', requisito.orden)
            requisito.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Requisito actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_costo_api(request):
    """API para actualizar costos"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        costo_id = data.get('costo_id')
        tramite_id = data.get('tramite_id')
        
        if costo_id:
            # Actualizar costo existente
            costo = get_object_or_404(TramiteCosto, id=costo_id)
            tramite = costo.tramite
        elif tramite_id:
            # Crear nuevo costo
            tramite = get_object_or_404(Tramite, id=tramite_id)
            costo = TramiteCosto.objects.create(
                tramite=tramite,
                concepto=data.get('concepto', ''),
                importe=data.get('importe', 0.0000),
                unidad_valor=data.get('unidad_valor', ''),
                fundamento_juridico=data.get('fundamento_juridico', ''),
                orden=data.get('orden', 0)
            )
        else:
            return JsonResponse({'error': 'ID de costo o trámite requerido'}, status=400)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar costo
        if costo_id:
            costo.concepto = data.get('concepto', costo.concepto)
            costo.importe = data.get('importe', costo.importe)
            costo.unidad_valor = data.get('unidad_valor', costo.unidad_valor)
            costo.fundamento_juridico = data.get('fundamento_juridico', costo.fundamento_juridico)
            costo.orden = data.get('orden', costo.orden)
            costo.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Costo actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_opcion_pago_api(request):
    """API para actualizar opciones de pago"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        opcion_id = data.get('opcion_id')
        tramite_id = data.get('tramite_id')
        
        if opcion_id:
            # Actualizar opción existente
            opcion = get_object_or_404(TramiteOpcionPago, id=opcion_id)
            tramite = opcion.tramite
        elif tramite_id:
            # Crear nueva opción
            tramite = get_object_or_404(Tramite, id=tramite_id)
            opcion = TramiteOpcionPago.objects.create(
                tramite=tramite,
                descripcion=data.get('descripcion', ''),
                observacion=data.get('observacion', ''),
                orden=data.get('orden', 0)
            )
        else:
            return JsonResponse({'error': 'ID de opción o trámite requerido'}, status=400)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar opción
        if opcion_id:
            opcion.descripcion = data.get('descripcion', opcion.descripcion)
            opcion.observacion = data.get('observacion', opcion.observacion)
            opcion.orden = data.get('orden', opcion.orden)
            opcion.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Opción de pago actualizada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_fundamento_juridico_api(request):
    """API para actualizar fundamentos jurídicos"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        fundamento_id = data.get('fundamento_id')
        tramite_id = data.get('tramite_id')
        
        if fundamento_id:
            # Actualizar fundamento existente
            fundamento = get_object_or_404(TramiteFundamentoJuridico, id=fundamento_id)
            tramite = fundamento.tramite
        elif tramite_id:
            # Crear nuevo fundamento
            tramite = get_object_or_404(Tramite, id=tramite_id)
            fundamento = TramiteFundamentoJuridico.objects.create(
                tramite=tramite,
                nombre_ley=data.get('nombre_ley', ''),
                articulos=data.get('articulos', ''),
                orden=data.get('orden', 0)
            )
        else:
            return JsonResponse({'error': 'ID de fundamento o trámite requerido'}, status=400)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar fundamento
        if fundamento_id:
            fundamento.nombre_ley = data.get('nombre_ley', fundamento.nombre_ley)
            fundamento.articulos = data.get('articulos', fundamento.articulos)
            fundamento.orden = data.get('orden', fundamento.orden)
            fundamento.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Fundamento jurídico actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_informacion_adicional_api(request):
    """API para actualizar información adicional"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        info_id = data.get('info_id')
        tramite_id = data.get('tramite_id')
        
        if info_id:
            # Actualizar información existente
            info = get_object_or_404(TramiteInformacionAdicional, id=info_id)
            tramite = info.tramite
        elif tramite_id:
            # Crear nueva información
            tramite = get_object_or_404(Tramite, id=tramite_id)
            info = TramiteInformacionAdicional.objects.create(
                tramite=tramite,
                pregunta=data.get('pregunta', ''),
                respuesta=data.get('respuesta', ''),
                orden=data.get('orden', 0)
            )
        else:
            return JsonResponse({'error': 'ID de información o trámite requerido'}, status=400)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar información
        if info_id:
            info.pregunta = data.get('pregunta', info.pregunta)
            info.respuesta = data.get('respuesta', info.respuesta)
            info.orden = data.get('orden', info.orden)
            info.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Información adicional actualizada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_oficina_atencion_api(request):
    """API para actualizar oficinas de atención"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Debes iniciar sesión'}, status=403)
    
    try:
        data = json.loads(request.body)
        oficina_id = data.get('oficina_id')
        tramite_id = data.get('tramite_id')
        
        if oficina_id:
            # Actualizar oficina existente
            oficina = get_object_or_404(TramiteOficinaAtencion, id=oficina_id)
            tramite = oficina.tramite
        elif tramite_id:
            # Crear nueva oficina
            tramite = get_object_or_404(Tramite, id=tramite_id)
            oficina = TramiteOficinaAtencion.objects.create(
                tramite=tramite,
                nombre=data.get('nombre', ''),
                calle=data.get('calle', ''),
                numero_exterior=data.get('numero_exterior', ''),
                numero_interior=data.get('numero_interior', ''),
                colonia=data.get('colonia', ''),
                codigo_postal=data.get('codigo_postal', ''),
                horario_atencion=data.get('horario_atencion', ''),
                telefonos=data.get('telefonos', ''),
                celular=data.get('celular', ''),
                email_responsable=data.get('email_responsable', ''),
                nombre_responsable=data.get('nombre_responsable', ''),
                puesto_responsable=data.get('puesto_responsable', ''),
                latitud=data.get('latitud'),
                longitud=data.get('longitud'),
                orden=data.get('orden', 0)
            )
        else:
            return JsonResponse({'error': 'ID de oficina o trámite requerido'}, status=400)
        
        # Verificar permisos
        if not request.user.is_staff and not request.user.is_superuser:
            try:
                perfil = PerfilUsuario.objects.get(user=request.user)
                if perfil.clasificacion != tramite.clasificacion:
                    return JsonResponse({'error': 'No tienes permisos para editar este trámite'}, status=403)
            except PerfilUsuario.DoesNotExist:
                return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
        
        # Actualizar oficina
        if oficina_id:
            oficina.nombre = data.get('nombre', oficina.nombre)
            oficina.calle = data.get('calle', oficina.calle)
            oficina.numero_exterior = data.get('numero_exterior', oficina.numero_exterior)
            oficina.numero_interior = data.get('numero_interior', oficina.numero_interior)
            oficina.colonia = data.get('colonia', oficina.colonia)
            oficina.codigo_postal = data.get('codigo_postal', oficina.codigo_postal)
            oficina.horario_atencion = data.get('horario_atencion', oficina.horario_atencion)
            oficina.telefonos = data.get('telefonos', oficina.telefonos)
            oficina.celular = data.get('celular', oficina.celular)
            oficina.email_responsable = data.get('email_responsable', oficina.email_responsable)
            oficina.nombre_responsable = data.get('nombre_responsable', oficina.nombre_responsable)
            oficina.puesto_responsable = data.get('puesto_responsable', oficina.puesto_responsable)
            oficina.latitud = data.get('latitud', oficina.latitud)
            oficina.longitud = data.get('longitud', oficina.longitud)
            oficina.orden = data.get('orden', oficina.orden)
            oficina.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Oficina de atención actualizada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    
    
    # Agregar esta función a tu archivo views.py

from django.http import JsonResponse
from django.db.models import Q
import unicodedata
import re

def buscar_api(request):
    """
    API para buscar trámites y clasificaciones
    Busca en nombres de clasificaciones y trámites con tolerancia a acentos
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({
            'clasificaciones': [],
            'tramites': [],
            'total': 0
        })
    
    # Función para normalizar texto (quitar acentos)
    def normalizar_texto(texto):
        # Convertir a minúsculas y quitar acentos
        texto = texto.lower()
        return ''.join(c for c in unicodedata.normalize('NFD', texto)
                      if unicodedata.category(c) != 'Mn')
    
    # Normalizar la consulta
    query_normalizada = normalizar_texto(query)
    
    # Buscar en clasificaciones
    clasificaciones = ClasificacionTramites.objects.all()
    clasificaciones_encontradas = []
    
    for clasificacion in clasificaciones:
        nombre_normalizado = normalizar_texto(clasificacion.nombre)
        if query_normalizada in nombre_normalizado:
            clasificaciones_encontradas.append({
                'id': clasificacion.id,
                'nombre': clasificacion.nombre,
                'imagen': clasificacion.imagen.url if clasificacion.imagen else None,
                'tipo': 'clasificacion'
            })
    
    # Buscar en trámites activos
    tramites = Tramite.objects.filter(estatus='Activo').select_related('clasificacion')
    tramites_encontrados = []
    
    for tramite in tramites:
        nombre_normalizado = normalizar_texto(tramite.nombre)
        if query_normalizada in nombre_normalizado:
            tramites_encontrados.append({
                'id': tramite.id,
                'nombre': tramite.nombre,
                'descripcion': tramite.descripcion[:150] + '...' if len(tramite.descripcion) > 150 else tramite.descripcion,
                'clasificacion_id': tramite.clasificacion.id,
                'clasificacion_nombre': tramite.clasificacion.nombre,
                'tipo': 'tramite'
            })
    
    # Limitar resultados
    clasificaciones_encontradas = clasificaciones_encontradas[:10]
    tramites_encontrados = tramites_encontrados[:20]
    
    total = len(clasificaciones_encontradas) + len(tramites_encontrados)
    
    return JsonResponse({
        'clasificaciones': clasificaciones_encontradas,
        'tramites': tramites_encontrados,
        'total': total,
        'query': query
    })


def protesta_view(request):
    """Vista para manejar protestas ciudadanas"""
    
    # Obtener datos del trámite si viene tramite_id
    tramite = None
    tramite_id = request.GET.get('tramite_id')
    
    if tramite_id:
        try:
            tramite = get_object_or_404(Tramite, id=tramite_id)
        except:
            tramite = None
    
    # Si es POST, procesar el formulario de protesta
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            data = request.POST
            files = request.FILES
            
            # Validar campos obligatorios
            required_fields = [
                'clv_motivo', 'folio_referencia', 'fecha_tramite', 'hora_tramite',
                'rfc', 'calificacion_afectacion', 'costo_afectacion', 'costo_letra_afectacion',
                'empleos_afectacion', 'nombre', 'apellido_paterno', 'apellido_materno',
                'estado', 'municipio', 'calle', 'num_ext', 'colonia', 'codigo_postal',
                'email', 'telefono', 'descripcion_protesta', 'servidor_publico'
            ]
            
            for field in required_fields:
                if not data.get(field, '').strip():
                    return JsonResponse({
                        'success': False,
                        'error': f'El campo {field} es obligatorio'
                    })
            
            # Obtener el trámite
            tramite_id = data.get('tramite_id')
            if tramite_id:
                tramite = get_object_or_404(Tramite, id=tramite_id)
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Trámite requerido'
                })
            
            # Crear la protesta
            protesta = ProtestaCiudadana.objects.create(
                # Datos del trámite
                tramite=tramite,
                area=data.get('area', ''),
                responsable=data.get('responsable', ''),
                nombre_tramite=data.get('nombre_tramite', ''),
                objeto_protesta=data.get('objeto_protesta', ''),
                
                # Datos del motivo y procedimiento
                clv_motivo=int(data.get('clv_motivo')),
                tipo_tramite=data.get('tipo_tramite', 'C'),
                folio_referencia=data.get('folio_referencia'),
                es_presencial=int(data.get('es_presencial', 1)),
                lugar_administrativa=data.get('lugar_administrativa', ''),
                liga_internet=data.get('liga_internet', ''),
                fecha_tramite=data.get('fecha_tramite'),
                hora_tramite=data.get('hora_tramite'),
                
                # Datos económicos
                rfc=data.get('rfc').upper(),
                calificacion_afectacion=int(data.get('calificacion_afectacion', 1)),
                costo_afectacion=float(data.get('costo_afectacion', 0)),
                costo_letra_afectacion=data.get('costo_letra_afectacion'),
                empleos_afectacion=int(data.get('empleos_afectacion', 0)),
                
                # Datos personales
                nombre=data.get('nombre').upper(),
                apellido_paterno=data.get('apellido_paterno').upper(),
                apellido_materno=data.get('apellido_materno').upper(),
                estado=data.get('estado').upper(),
                municipio=data.get('municipio').upper(),
                calle=data.get('calle').upper(),
                num_ext=data.get('num_ext').upper(),
                num_int=data.get('num_int', '').upper(),
                colonia=data.get('colonia').upper(),
                codigo_postal=data.get('codigo_postal'),
                referencias_domicilio=data.get('referencias_domicilio', '').upper(),
                
                # Datos de contacto
                email=data.get('email'),
                telefono=data.get('telefono'),
                movil=data.get('movil', ''),
                
                # Descripción y servidor
                descripcion_protesta=data.get('descripcion_protesta').upper(),
                servidor_publico=data.get('servidor_publico').upper(),
                
                # Archivos
                archivo_identificacion=files.get('archivo_identificacion'),
                archivo_comprobante_dom=files.get('archivo_comprobante_dom'),
                evidencia=files.get('evidencia'),
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Protesta ciudadana enviada exitosamente',
                'folio': protesta.folio,
                'protesta_id': protesta.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error al procesar la protesta: {str(e)}'
            })
    
    # Si es GET con folio_busqueda, buscar protesta
    folio_busqueda = request.GET.get('folio_busqueda')
    protesta_encontrada = None
    
    if folio_busqueda:
        try:
            protesta_encontrada = ProtestaCiudadana.objects.get(folio=folio_busqueda.strip().upper())
        except ProtestaCiudadana.DoesNotExist:
            protesta_encontrada = None
    
    context = {
        'tramite': tramite,
        'protesta_encontrada': protesta_encontrada,
        'folio_busqueda': folio_busqueda,
    }
    
    return render(request, 'protesta.html', context)


@csrf_exempt
@require_http_methods(["GET"])
def get_protestas_api(request):
    """API para obtener todas las protestas (solo superuser)"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        # Obtener parámetros de búsqueda y filtros
        page = int(request.GET.get('page', 1))
        search = request.GET.get('search', '').strip()
        status_filter = request.GET.get('status', '').strip()
        per_page = 10
        
        # Construir queryset base ordenado por más recientes
        protestas = ProtestaCiudadana.objects.select_related('tramite').order_by('-fecha_creacion')
        
        # Aplicar filtros
        if search:
            protestas = protestas.filter(
                models.Q(folio__icontains=search) |
                models.Q(nombre__icontains=search) |
                models.Q(apellido_paterno__icontains=search) |
                models.Q(apellido_materno__icontains=search) |
                models.Q(rfc__icontains=search)
            )
        
        if status_filter:
            protestas = protestas.filter(estatus=status_filter)
        
        # Paginación
        paginator = Paginator(protestas, per_page)
        page_obj = paginator.get_page(page)
        
        # Preparar datos
        protestas_data = []
        for protesta in page_obj:
            protestas_data.append({
                'id': protesta.id,
                'folio': protesta.folio,
                'nombre_completo': protesta.get_nombre_completo(),
                'tramite_nombre': protesta.nombre_tramite,
                'area': protesta.area,
                'estatus': protesta.estatus,
                'estatus_display': protesta.get_estatus_display(),
                'fecha_creacion': protesta.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'motivo_display': protesta.get_motivo_display_text(),
                'email': protesta.email,
                'telefono': protesta.telefono,
                'servidor_publico': protesta.servidor_publico,
            })
        
        return JsonResponse({
            'protestas': protestas_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            },
            'status_choices': [
                {'value': choice[0], 'label': choice[1]} 
                for choice in ProtestaCiudadana.ESTATUS_CHOICES
            ]
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_protesta_status_api(request):
    """API para actualizar el estatus de una protesta (solo superuser)"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        data = json.loads(request.body)
        protesta_id = data.get('protesta_id')
        nuevo_estatus = data.get('estatus')
        
        if not protesta_id or not nuevo_estatus:
            return JsonResponse({'error': 'ID de protesta y estatus requeridos'}, status=400)
        
        # Validar que el estatus sea válido
        estatus_validos = [choice[0] for choice in ProtestaCiudadana.ESTATUS_CHOICES]
        if nuevo_estatus not in estatus_validos:
            return JsonResponse({'error': 'Estatus inválido'}, status=400)
        
        protesta = get_object_or_404(ProtestaCiudadana, id=protesta_id)
        estatus_anterior = protesta.estatus
        protesta.estatus = nuevo_estatus
        protesta.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Estatus cambiado de "{protesta.get_estatus_display()}" a "{dict(ProtestaCiudadana.ESTATUS_CHOICES)[nuevo_estatus]}"',
            'protesta': {
                'id': protesta.id,
                'folio': protesta.folio,
                'estatus': protesta.estatus,
                'estatus_display': protesta.get_estatus_display()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Reemplaza la función generar_protesta_pdf completa con esta versión corregida:

@require_http_methods(["GET"])
def generar_protesta_pdf(request, protesta_id):
    """Generar PDF completo de una protesta (solo superuser)"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        protesta = get_object_or_404(ProtestaCiudadana, id=protesta_id)
        
        # Crear respuesta HTTP para PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Protesta_{protesta.folio}.pdf"'
        
        # Crear el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.darkblue,
            borderColor=colors.darkblue,
            borderWidth=1,
            borderPadding=5,
            backColor=colors.lightgrey
        )
        
        # Estilo para texto en celdas
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=0,
            leftIndent=0,
            wordWrap='CJK'
        )
        
        # Función auxiliar para crear texto que se ajuste a la celda
        def create_cell_paragraph(text, style=cell_style):
            return Paragraph(str(text), style)
        
        # Contenido del PDF
        content = []
        
        # Título
        content.append(Paragraph("PROTESTA CIUDADANA", title_style))
        content.append(Paragraph(f"Folio: {protesta.folio}", styles['Heading2']))
        content.append(Spacer(1, 20))
        
        # Información de Control
        content.append(Paragraph("INFORMACIÓN DE CONTROL", heading_style))
        info_control = [
            [create_cell_paragraph('Folio:'), create_cell_paragraph(protesta.folio)],
            [create_cell_paragraph('Fecha de Creación:'), create_cell_paragraph(protesta.fecha_creacion.strftime('%d/%m/%Y %H:%M:%S'))],
            [create_cell_paragraph('Estatus:'), create_cell_paragraph(protesta.get_estatus_display())],
        ]
        
        table = Table(info_control, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Datos del Trámite
        content.append(Paragraph("DATOS DEL TRÁMITE", heading_style))
        datos_tramite = [
            [create_cell_paragraph('Área:'), create_cell_paragraph(protesta.area)],
            [create_cell_paragraph('Responsable:'), create_cell_paragraph(protesta.responsable)],
            [create_cell_paragraph('Nombre del Trámite:'), create_cell_paragraph(protesta.nombre_tramite)],
            [create_cell_paragraph('Objeto de Protesta:'), create_cell_paragraph(protesta.objeto_protesta)],
        ]
        
        table = Table(datos_tramite, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Motivo y Procedimiento
        content.append(Paragraph("MOTIVO Y PROCEDIMIENTO", heading_style))
        motivo_proc = [
            [create_cell_paragraph('Motivo:'), create_cell_paragraph(protesta.get_motivo_display_text())],
            [create_cell_paragraph('Tipo de Trámite:'), create_cell_paragraph(protesta.get_tipo_tramite_display())],
            [create_cell_paragraph('Folio de Referencia:'), create_cell_paragraph(protesta.folio_referencia)],
            [create_cell_paragraph('¿Es Presencial?:'), create_cell_paragraph('Sí' if protesta.es_presencial == 1 else 'No')],
            [create_cell_paragraph('Lugar/Liga:'), create_cell_paragraph(protesta.lugar_administrativa if protesta.es_presencial == 1 else protesta.liga_internet)],
            [create_cell_paragraph('Fecha del Trámite:'), create_cell_paragraph(protesta.fecha_tramite.strftime('%d/%m/%Y'))],
            [create_cell_paragraph('Hora del Trámite:'), create_cell_paragraph(protesta.hora_tramite.strftime('%H:%M'))],
        ]
        
        table = Table(motivo_proc, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Información Económica
        content.append(Paragraph("INFORMACIÓN ECONÓMICA", heading_style))
        info_economica = [
            [create_cell_paragraph('RFC:'), create_cell_paragraph(protesta.rfc)],
            [create_cell_paragraph('Calificación de Afectación:'), create_cell_paragraph(f'{protesta.calificacion_afectacion}/10')],
            [create_cell_paragraph('Costo de Afectación:'), create_cell_paragraph(f'${protesta.costo_afectacion:,.2f} MXN')],
            [create_cell_paragraph('Costo con Letra:'), create_cell_paragraph(protesta.costo_letra_afectacion)],
            [create_cell_paragraph('Empleos Afectados:'), create_cell_paragraph(str(protesta.empleos_afectacion))],
        ]
        
        table = Table(info_economica, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Datos Personales
        content.append(Paragraph("DATOS PERSONALES DEL SOLICITANTE", heading_style))
        direccion_completa = f'{protesta.calle} #{protesta.num_ext}' + (f' Int. {protesta.num_int}' if protesta.num_int else '')
        datos_personales = [
            [create_cell_paragraph('Nombre Completo:'), create_cell_paragraph(protesta.get_nombre_completo())],
            [create_cell_paragraph('Estado:'), create_cell_paragraph(protesta.estado)],
            [create_cell_paragraph('Municipio:'), create_cell_paragraph(protesta.municipio)],
            [create_cell_paragraph('Dirección:'), create_cell_paragraph(direccion_completa)],
            [create_cell_paragraph('Colonia:'), create_cell_paragraph(protesta.colonia)],
            [create_cell_paragraph('Código Postal:'), create_cell_paragraph(protesta.codigo_postal)],
            [create_cell_paragraph('Referencias:'), create_cell_paragraph(protesta.referencias_domicilio or 'N/A')],
        ]
        
        table = Table(datos_personales, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Datos de Contacto
        content.append(Paragraph("DATOS DE CONTACTO", heading_style))
        contacto = [
            [create_cell_paragraph('Email:'), create_cell_paragraph(protesta.email)],
            [create_cell_paragraph('Teléfono:'), create_cell_paragraph(protesta.telefono)],
            [create_cell_paragraph('Móvil:'), create_cell_paragraph(protesta.movil or 'N/A')],
        ]
        
        table = Table(contacto, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Descripción de la Protesta
        content.append(Paragraph("DESCRIPCIÓN DE LA PROTESTA", heading_style))
        
        descripcion_data = [
            [create_cell_paragraph('Servidor Público:'), create_cell_paragraph(protesta.servidor_publico)],
            [create_cell_paragraph('Descripción:'), create_cell_paragraph(protesta.descripcion_protesta)],
        ]
        
        table = Table(descripcion_data, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        content.append(Spacer(1, 20))
        
        # Archivos Adjuntos
        content.append(Paragraph("ARCHIVOS ADJUNTOS", heading_style))
        archivos = [
            [create_cell_paragraph('Identificación:'), create_cell_paragraph('Sí' if protesta.archivo_identificacion else 'No')],
            [create_cell_paragraph('Comprobante Domicilio:'), create_cell_paragraph('Sí' if protesta.archivo_comprobante_dom else 'No')],
            [create_cell_paragraph('Evidencia:'), create_cell_paragraph('Sí' if protesta.evidencia else 'No')],
        ]
        
        table = Table(archivos, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        content.append(table)
        
        # Construir el PDF
        doc.build(content)
        
        # Obtener el PDF del buffer
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        
        return response
        
    except Exception as e:
        return JsonResponse({'error': f'Error al generar PDF: {str(e)}'}, status=500)
    
    
# Agregar estas funciones al final de tu views.py existente

@csrf_exempt
@require_http_methods(["GET"])
def get_grupos_api(request):
    """API para obtener todos los grupos y sus usuarios (solo superadmin)"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        # Obtener todos los usuarios con sus perfiles
        usuarios = User.objects.select_related('perfilusuario').all()
        
        # Organizar usuarios por grupo
        grupos = {
            'SUPER_ADMIN': [],
            'ADMINISTRADOR': [],
            'GESTOR_PROTESTAS': [],
            'GESTOR_TRAMITES': []
        }
        
        for user in usuarios:
            try:
                perfil = user.perfilusuario
                grupo = perfil.grupo_usuario
                
                # Asegurar que superusers estén en SUPER_ADMIN
                if user.is_superuser:
                    grupo = 'SUPER_ADMIN'
                    if perfil.grupo_usuario != 'SUPER_ADMIN':
                        perfil.grupo_usuario = 'SUPER_ADMIN'
                        perfil.save()
                
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'nombre_completo': f'{user.first_name} {user.last_name}'.strip() or user.username,
                    'email': user.email,
                    'area': perfil.clasificacion.nombre if perfil.clasificacion else 'Sin área asignada',
                    'is_active': user.is_active,
                    'fecha_registro': user.date_joined.strftime('%d/%m/%Y')
                }
                
                # Agregar al grupo correspondiente
                if grupo in grupos:
                    grupos[grupo].append(user_data)
                else:
                    # Si no tiene grupo válido, asignar a GESTOR_TRAMITES por defecto
                    grupos['GESTOR_TRAMITES'].append(user_data)
                    perfil.grupo_usuario = 'GESTOR_TRAMITES'
                    perfil.save()
                    
            except PerfilUsuario.DoesNotExist:
                # Si no tiene perfil, crear uno
                grupo = 'SUPER_ADMIN' if user.is_superuser else 'GESTOR_TRAMITES'
                PerfilUsuario.objects.create(user=user, grupo_usuario=grupo)
                
                user_data = {
                    'id': user.id,
                    'username': user.username,
                    'nombre_completo': f'{user.first_name} {user.last_name}'.strip() or user.username,
                    'email': user.email,
                    'area': 'Sin área asignada',
                    'is_active': user.is_active,
                    'fecha_registro': user.date_joined.strftime('%d/%m/%Y')
                }
                grupos[grupo].append(user_data)
        
        return JsonResponse({
            'grupos': grupos,
            'totales': {
                'SUPER_ADMIN': len(grupos['SUPER_ADMIN']),
                'ADMINISTRADOR': len(grupos['ADMINISTRADOR']),
                'GESTOR_PROTESTAS': len(grupos['GESTOR_PROTESTAS']),
                'GESTOR_TRAMITES': len(grupos['GESTOR_TRAMITES'])
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def cambiar_grupo_usuario_api(request):
    """API para cambiar el grupo de un usuario (solo superadmin)"""
    if not request.user.is_authenticated or not request.user.is_superuser:
        return JsonResponse({'error': 'No tienes permisos para esta acción'}, status=403)
    
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        nuevo_grupo = data.get('nuevo_grupo')
        
        if not user_id or not nuevo_grupo:
            return JsonResponse({'error': 'ID de usuario y nuevo grupo requeridos'}, status=400)
        
        # Validar que el grupo sea válido
        grupos_validos = ['SUPER_ADMIN', 'ADMINISTRADOR', 'GESTOR_PROTESTAS', 'GESTOR_TRAMITES']
        if nuevo_grupo not in grupos_validos:
            return JsonResponse({'error': 'Grupo inválido'}, status=400)
        
        user = get_object_or_404(User, id=user_id)
        
        # No permitir cambiar el grupo del propio superuser que está logueado
        if user.id == request.user.id:
            return JsonResponse({'error': 'No puedes cambiar tu propio grupo'}, status=400)
        
        # Obtener o crear perfil
        try:
            perfil = user.perfilusuario
        except PerfilUsuario.DoesNotExist:
            perfil = PerfilUsuario.objects.create(user=user)
        
        grupo_anterior = perfil.grupo_usuario
        
        # Validaciones especiales
        if nuevo_grupo == 'SUPER_ADMIN' and not user.is_superuser:
            return JsonResponse({'error': 'Solo usuarios superuser pueden estar en el grupo SUPER_ADMIN'}, status=400)
        
        # Actualizar el grupo
        perfil.grupo_usuario = nuevo_grupo
        perfil.save()
        
        # Mapeo de nombres de grupos para el mensaje
        grupos_display = {
            'SUPER_ADMIN': 'Super Administrador',
            'ADMINISTRADOR': 'Administrador',
            'GESTOR_PROTESTAS': 'Gestor de Protestas',
            'GESTOR_TRAMITES': 'Gestor de Trámites'
        }
        
        return JsonResponse({
            'success': True,
            'message': f'Usuario {user.username} movido de "{grupos_display.get(grupo_anterior, grupo_anterior)}" a "{grupos_display.get(nuevo_grupo, nuevo_grupo)}"',
            'user': {
                'id': user.id,
                'username': user.username,
                'grupo_anterior': grupo_anterior,
                'grupo_nuevo': nuevo_grupo
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# También necesitas actualizar la función get_users_api existente para incluir el grupo
# Reemplaza la función get_users_api con esta versión actualizada:

@csrf_exempt
@require_http_methods(["GET"])
def get_users_api(request):
    """API para obtener todos los usuarios (solo superadmin) - VERSIÓN ACTUALIZADA"""
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
                grupo_usuario = perfil.grupo_usuario
            except PerfilUsuario.DoesNotExist:
                clasificacion_id = None
                clasificacion_nombre = 'Sin perfil'
                grupo_usuario = 'GESTOR_TRAMITES'
            
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
                'grupo_usuario': grupo_usuario,
                'date_joined': user.date_joined.strftime('%d/%m/%Y')
            })
        
        clasificaciones_data = [{'id': c.id, 'nombre': c.nombre} for c in clasificaciones]
        
        return JsonResponse({
            'users': users_data,
            'clasificaciones': clasificaciones_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# También actualiza la función create_user_api para asignar grupo automáticamente:

@csrf_exempt
@require_http_methods(["POST"])
def create_user_api(request):
    """API para crear un nuevo usuario (solo superadmin) - VERSIÓN ACTUALIZADA"""
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
        
        # Obtener o crear perfil
        try:
            perfil = PerfilUsuario.objects.get(user=user)
        except PerfilUsuario.DoesNotExist:
            # Determinar grupo automáticamente
            grupo = 'SUPER_ADMIN' if user.is_superuser else 'GESTOR_TRAMITES'
            perfil = PerfilUsuario.objects.create(user=user, grupo_usuario=grupo)
        
        # Asignar clasificación si se proporciona
        clasificacion_id = data.get('clasificacion_id')
        if clasificacion_id:
            try:
                clasificacion = ClasificacionTramites.objects.get(id=clasificacion_id)
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