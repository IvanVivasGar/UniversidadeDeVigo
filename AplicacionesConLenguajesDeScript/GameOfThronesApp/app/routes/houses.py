from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app.models.house import House
from app.models.character import Character
from app.models.event import Event
from app.utils.helpers import get_entity_by_name, search_entities, save_uploaded_file
import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

bp = Blueprint('houses', __name__)

@bp.route('/')
def houses():
    """Página principal de casas con búsqueda"""
    search_term = request.args.get('search', '')
    
    try:
        houses_list = search_entities(current_app.sirope, House, search_term)
        return render_template('houses/houses.html', 
                             houses=houses_list, 
                             search_term=search_term)
    except Exception as e:
        print(f"Error cargando casas: {e}")
        return render_template('houses/houses.html', 
                             houses=[], 
                             search_term=search_term)

@bp.route('/<house_id>')
def house_detail(house_id):
    """Página de detalle de una casa"""
    try:
        house_oid = sirope.OID.from_text(house_id)
        house = current_app.sirope.load(house_oid)
        
        if not house:
            flash('Casa no encontrada', 'error')
            return redirect(url_for('houses.houses'))
        
        # Obtener miembros de la casa
        members = []
        for member_oid in house.members:
            try:
                member = current_app.sirope.load(member_oid)
                if member:
                    members.append(member)
            except:
                continue
        
        # Obtener eventos relacionados
        events = []
        for event_oid in house.events:
            try:
                event = current_app.sirope.load(event_oid)
                if event:
                    events.append(event)
            except:
                continue
        
        return render_template('houses/house_detail.html', 
                             house=house, 
                             members=members,
                             events=events)
                             
    except Exception as e:
        print(f"Error cargando detalle de la casa: {e}")
        flash('Error cargando la casa', 'error')
        return redirect(url_for('houses.houses'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_house():
    """Crear nueva casa"""
    if request.method == 'POST':
        # Detectar si es una petición AJAX
        is_ajax = request.headers.get('Content-Type') == 'multipart/form-data' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        name = request.form.get('name')
        motto = request.form.get('motto')
        description = request.form.get('description')
        region = request.form.get('region')
        status = request.form.get('status')
        sigil_url = request.form.get('sigil_url')
        
        if not name or not description or not region or not status:
            if is_ajax:
                return jsonify({'success': False, 'message': 'Los campos obligatorios son requeridos'})
            flash('Los campos obligatorios son requeridos', 'error')
            return redirect(url_for('houses.create_house'))
        
        try:
            # Verificar que la casa no exista
            existing_house = get_entity_by_name(current_app.sirope, House, name)
            if existing_house:
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Ya existe una casa con ese nombre'})
                flash('Ya existe una casa con ese nombre', 'error')
                return redirect(url_for('houses.create_house'))
            
            # Procesar imagen principal
            image_urls = []
            if sigil_url:
                image_urls.append(sigil_url)
            elif 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    image_url = save_uploaded_file(file, 'houses')
                    if image_url:
                        image_urls.append(image_url)
            
            # Crear casa con los nuevos campos (usar 'images' en lugar de 'image_urls')
            house = House(name, motto or "", description, image_urls)
            house.region = region
            house.status = status
            
            oid = current_app.sirope.save(house)
            
            if is_ajax:
                return jsonify({
                    'success': True, 
                    'message': 'Casa creada exitosamente',
                    'house_id': str(oid),
                    'redirect_url': url_for('houses.house_detail', house_id=str(oid))
                })
            
            flash('Casa creada exitosamente', 'success')
            return redirect(url_for('houses.house_detail', house_id=str(oid)))
            
        except Exception as e:
            print(f"Error creando casa: {e}")
            if is_ajax:
                return jsonify({'success': False, 'message': 'Error creando la casa'})
            flash('Error creando la casa', 'error')
    
    return render_template('houses/create_house.html')

@bp.route('/<house_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_house(house_id):
    """Editar casa existente - Reutiliza el template de creación"""
    try:
        house_oid = sirope.OID.from_text(house_id)
        house = current_app.sirope.load(house_oid)
        
        if not house:
            flash('Casa no encontrada', 'error')
            return redirect(url_for('houses.houses'))
        
        if request.method == 'POST':
            # Detectar si es una petición AJAX
            is_ajax = request.headers.get('Content-Type') == 'multipart/form-data' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            name = request.form.get('name')
            motto = request.form.get('motto')
            description = request.form.get('description')
            region = request.form.get('region')
            status = request.form.get('status')
            sigil_url = request.form.get('sigil_url')
            
            if not name or not description or not region or not status:
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Los campos obligatorios son requeridos'})
                flash('Los campos obligatorios son requeridos', 'error')
                return redirect(url_for('houses.edit_house', house_id=house_id))
            
            # Verificar nombre único (excepto la actual)
            existing_house = get_entity_by_name(current_app.sirope, House, name)
            if existing_house and existing_house.__oid__ != house_oid:
                if is_ajax:
                    return jsonify({'success': False, 'message': 'Ya existe una casa con ese nombre'})
                flash('Ya existe una casa con ese nombre', 'error')
                return redirect(url_for('houses.edit_house', house_id=house_id))
            
            # Actualizar datos
            house.name = name
            house.motto = motto or ""
            house.description = description
            house.region = region
            house.status = status
            
            # Procesar nueva imagen principal
            if sigil_url:
                # Si hay URL, reemplazar la primera imagen o agregar
                if house.images:
                    house.images[0] = sigil_url
                else:
                    house.add_image(sigil_url)
            elif 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    image_url = save_uploaded_file(file, 'houses')
                    if image_url:
                        if house.images:
                            house.images[0] = image_url
                        else:
                            house.add_image(image_url)
            
            current_app.sirope.save(house)
            
            if is_ajax:
                return jsonify({
                    'success': True, 
                    'message': 'Casa actualizada exitosamente',
                    'house_id': str(house_oid),
                    'redirect_url': url_for('houses.houses')
                })
            
            flash('Casa actualizada exitosamente', 'success')
            return redirect(url_for('houses.houses'))
        
        # GET request - mostrar formulario con datos de la casa
        return render_template('houses/create_house.html', 
                             house=house, 
                             editing=True)
                             
    except Exception as e:
        print(f"Error editando casa: {e}")
        flash('Error cargando la casa', 'error')
        return redirect(url_for('houses.houses'))

@bp.route('/<house_id>/rate', methods=['POST'])
@login_required
def rate_house(house_id):
    """Calificar una casa"""
    try:
        data = request.get_json()
        rating = int(data.get('rating', 0))
        
        if not (1 <= rating <= 5):
            return jsonify({'success': False, 'message': 'Rating debe estar entre 1 y 5'})
        
        house_oid = sirope.OID.from_text(house_id)
        house = current_app.sirope.load(house_oid)
        
        if not house:
            return jsonify({'success': False, 'message': 'Casa no encontrada'})
        
        # Verificar si el usuario ya calificó esta casa
        user_rating = current_user.get_rating_for(house_oid)
        
        if user_rating:
            # Actualizar rating existente
            # Remover rating anterior del promedio
            house.ratings.remove(user_rating)
            house.rating_count = len(house.ratings)
            house.total_rating = sum(house.ratings) / house.rating_count if house.rating_count > 0 else 0
            
            # Actualizar rating del usuario
            current_user.update_rating(house_oid, rating)
        else:
            # Agregar nuevo rating
            current_user.add_rating(house_oid, rating)
        
        # Agregar nuevo rating a la casa
        house.add_rating(rating)
        
        current_app.sirope.save(house)
        current_app.sirope.save(current_user)
        
        return jsonify({
            'success': True, 
            'message': 'Calificación actualizada exitosamente',
            'new_average': house.get_average_rating(),
            'total_ratings': house.rating_count,
            'user_rating': rating
        })
        
    except Exception as e:
        print(f"Error calificando casa: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<house_id>/user-rating', methods=['GET'])
@login_required
def get_user_rating(house_id):
    """Obtener la calificación del usuario actual para una casa"""
    try:
        house_oid = sirope.OID.from_text(house_id)
        user_rating = current_user.get_rating_for(house_oid)
        
        return jsonify({
            'user_rating': user_rating or 0
        })
        
    except Exception as e:
        print(f"Error obteniendo rating del usuario: {e}")
        return jsonify({'user_rating': 0})

@bp.route('/<house_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite_house(house_id):
    """Agregar o quitar casa de favoritos"""
    try:
        house_oid = sirope.OID.from_text(house_id)
        house = current_app.sirope.load(house_oid)
        
        if not house:
            return jsonify({'success': False, 'message': 'Casa no encontrada'})
        
        # Toggle favorite status
        is_favorite = current_user.toggle_favorite(house_oid)
        
        # Update house favorite count if the model supports it
        if hasattr(house, 'favorite_count'):
            if is_favorite:
                house.favorite_count = getattr(house, 'favorite_count', 0) + 1
            else:
                house.favorite_count = max(0, getattr(house, 'favorite_count', 1) - 1)
            current_app.sirope.save(house)
        
        current_app.sirope.save(current_user)
        
        message = f'Casa {house.name} agregada a favoritos' if is_favorite else f'Casa {house.name} removida de favoritos'
        
        return jsonify({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
        
    except Exception as e:
        print(f"Error en favoritos: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<house_id>/favorite-status', methods=['GET'])
@login_required
def get_favorite_status(house_id):
    """Obtener estado de favorito de una casa"""
    try:
        house_oid = sirope.OID.from_text(house_id)
        is_favorite = current_user.is_favorite(house_oid)
        
        return jsonify({
            'is_favorite': is_favorite
        })
        
    except Exception as e:
        print(f"Error obteniendo estado de favorito: {e}")
        return jsonify({'is_favorite': False})