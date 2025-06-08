from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app.models.character import Character
from app.models.house import House
from app.utils.helpers import get_entity_by_name, search_entities, save_uploaded_file
import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

bp = Blueprint('characters', __name__)

@bp.route('/')
def characters():
    """Página principal de personajes con búsqueda"""
    search_term = request.args.get('search', '')
    
    try:
        characters_list = search_entities(current_app.sirope, Character, search_term)
        return render_template('characters/characters.html', 
                             characters=characters_list, 
                             search_term=search_term)
    except Exception as e:
        print(f"Error cargando personajes: {e}")
        return render_template('characters/characters.html', 
                             characters=[], 
                             search_term=search_term)

@bp.route('/<character_id>')
def character_detail(character_id):
    """Página de detalle de un personaje"""
    try:
        character_oid = sirope.OID.from_text(character_id)
        character = current_app.sirope.load(character_oid)
        
        if not character:
            flash('Personaje no encontrado', 'error')
            return redirect(url_for('characters.characters'))
        
        # Obtener información de la casa
        house = None
        house_name = None
        
        if character.house_affiliation:
            try:
                house = current_app.sirope.load(character.house_affiliation)
                if house:
                    house_name = house.name
            except Exception as e:
                print(f"Error cargando casa: {e}")
        
        return render_template('characters/character_detail.html', 
                             character=character, 
                             house=house,
                             house_name=house_name)
                             
    except Exception as e:
        print(f"Error cargando detalle del personaje: {e}")
        flash('Error cargando el personaje', 'error')
        return redirect(url_for('characters.characters'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_character():
    """Crear nuevo personaje"""
    if request.method == 'POST':
        name = request.form.get('name')
        status = request.form.get('status')
        house_id = request.form.get('house_affiliation')
        description = request.form.get('description')
        
        if not name or not status or not description:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        try:
            # Verificar que el personaje no exista
            existing_character = get_entity_by_name(current_app.sirope, Character, name)
            if existing_character:
                return jsonify({'success': False, 'message': 'Ya existe un personaje con ese nombre'})
            
            # Procesar casa
            house_oid = None
            if house_id:
                try:
                    house_oid = sirope.OID.from_text(house_id)
                except:
                    pass
            
            # Procesar imagen
            image_url = None
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    image_url = save_uploaded_file(file, 'characters')
            
            # Crear personaje
            character = Character(name, status, house_oid, description, image_url)
            oid = current_app.sirope.save(character)
            
            # Agregar personaje a la casa si tiene una
            if house_oid:
                try:
                    house = current_app.sirope.load(house_oid)
                    if house:
                        house.add_member(oid)
                        current_app.sirope.save(house)
                except:
                    pass
            
            return jsonify({
                'success': True, 
                'message': '¡Personaje creado exitosamente!',
                'character_id': str(oid)
            })
            
        except Exception as e:
            print(f"Error creando personaje: {e}")
            return jsonify({'success': False, 'message': 'Error creando el personaje'})
    
    # Obtener casas para el formulario
    try:
        houses = list(current_app.sirope.load_all(House))
    except:
        houses = []
    
    return render_template('characters/create_character.html', houses=houses)

@bp.route('/<character_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_character(character_id):
    """Editar personaje existente"""
    try:
        character_oid = sirope.OID.from_text(character_id)
        character = current_app.sirope.load(character_oid)
        
        if not character:
            flash('Personaje no encontrado', 'error')
            return redirect(url_for('characters.characters'))
        
        if request.method == 'POST':
            # Detectar si es una petición AJAX/JSON
            is_ajax = request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            name = request.form.get('name')
            status = request.form.get('status')
            house_id = request.form.get('house_affiliation')
            description = request.form.get('description')
            
            if not name or not status or not description:
                error_msg = 'Todos los campos son requeridos'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('characters.edit_character', character_id=character_id))
            
            # Verificar nombre único (excepto el actual)
            existing_character = get_entity_by_name(current_app.sirope, Character, name)
            if existing_character and existing_character.__oid__ != character_oid:
                error_msg = 'Ya existe un personaje con ese nombre'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('characters.edit_character', character_id=character_id))
            
            try:
                # Guardar la casa anterior para actualizar relaciones
                old_house_oid = character.house_affiliation
                
                # Actualizar datos del personaje
                character.name = name
                character.status = status
                character.description = description
                
                # Procesar casa nueva
                new_house_oid = None
                if house_id and house_id.strip():
                    try:
                        new_house_oid = sirope.OID.from_text(house_id)
                        # Verificar que la casa existe
                        test_house = current_app.sirope.load(new_house_oid)
                        if not test_house:
                            new_house_oid = None
                    except Exception as e:
                        print(f"Error procesando house_id {house_id}: {e}")
                        new_house_oid = None
                
                character.house_affiliation = new_house_oid
                
                # Procesar imagen si se subió una nueva
                if 'image' in request.files:
                    file = request.files['image']
                    if file.filename != '':
                        image_url = save_uploaded_file(file, 'characters')
                        if image_url:
                            character.image_url = image_url
                
                # Guardar el personaje primero
                current_app.sirope.save(character)
                print(f"Personaje guardado: {character.name}, Casa: {character.house_affiliation}")
                
                # Actualizar relaciones de casas solo si cambió la casa
                if old_house_oid != new_house_oid:
                    print(f"Actualizando relaciones de casa: {old_house_oid} -> {new_house_oid}")
                    
                    # Remover de casa anterior
                    if old_house_oid:
                        try:
                            old_house = current_app.sirope.load(old_house_oid)
                            if old_house and character_oid in old_house.members:
                                old_house.members.remove(character_oid)
                                current_app.sirope.save(old_house)
                                print(f"Removido de casa anterior: {old_house.name}")
                        except Exception as e:
                            print(f"Error removiendo de casa anterior: {e}")
                    
                    # Agregar a nueva casa
                    if new_house_oid:
                        try:
                            new_house = current_app.sirope.load(new_house_oid)
                            if new_house:
                                if character_oid not in new_house.members:
                                    new_house.add_member(character_oid)
                                    current_app.sirope.save(new_house)
                                    print(f"Agregado a nueva casa: {new_house.name}")
                        except Exception as e:
                            print(f"Error agregando a nueva casa: {e}")
                
                success_msg = 'Personaje actualizado exitosamente'
                if is_ajax:
                    return jsonify({
                        'success': True, 
                        'message': success_msg,
                        'character_id': str(character_oid),
                        'redirect_url': url_for('characters.character_detail', character_id=character_id)
                    })
                flash(success_msg, 'success')
                return redirect(url_for('characters.character_detail', character_id=character_id))
                
            except Exception as e:
                print(f"Error actualizando personaje: {e}")
                error_msg = 'Error actualizando el personaje'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('characters.edit_character', character_id=character_id))
        
        # GET request - mostrar formulario con datos del personaje
        try:
            houses = list(current_app.sirope.load_all(House))
        except Exception as e:
            print(f"Error cargando casas: {e}")
            houses = []
        
        return render_template('characters/create_character.html', 
                             character=character, 
                             houses=houses, 
                             editing=True)
                             
    except Exception as e:
        print(f"Error editando personaje: {e}")
        flash('Error cargando el personaje', 'error')
        return redirect(url_for('characters.characters'))

@bp.route('/<character_id>/rate', methods=['POST'])
@login_required
def rate_character(character_id):
    """Calificar un personaje"""
    try:
        # Handle both form data and JSON
        if request.is_json:
            rating = int(request.json.get('rating', 0))
        else:
            rating = int(request.form.get('rating', 0))
        
        if not (1 <= rating <= 5):
            return jsonify({'success': False, 'message': 'Rating debe estar entre 1 y 5'})
        
        character_oid = sirope.OID.from_text(character_id)
        character = current_app.sirope.load(character_oid)
        
        if not character:
            return jsonify({'success': False, 'message': 'Personaje no encontrado'})
        
        # Verificar si el usuario ya calificó
        existing_rating = current_user.get_rating_for(character_oid)
        
        if existing_rating:
            # Usuario ya calificó - actualizar la valoración
            old_rating = existing_rating
            character.update_rating(old_rating, rating)
            current_user.update_rating(character_oid, rating)
            message = 'Calificación actualizada exitosamente'
        else:
            # Nueva calificación
            character.add_rating(rating)
            current_user.add_rating(character_oid, rating)
            message = 'Calificación agregada exitosamente'
        
        current_app.sirope.save(character)
        current_app.sirope.save(current_user)
        
        return jsonify({
            'success': True, 
            'message': message,
            'new_average': character.get_average_rating(),
            'total_ratings': character.rating_count,
            'user_rating': rating
        })
        
    except Exception as e:
        print(f"Error calificando personaje: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<character_id>/user-rating', methods=['GET'])
@login_required
def get_user_rating(character_id):
    """Obtener la valoración del usuario actual para un personaje"""
    try:
        character_oid = sirope.OID.from_text(character_id)
        user_rating = current_user.get_rating_for(character_oid)
        
        return jsonify({
            'success': True,
            'user_rating': user_rating
        })
        
    except Exception as e:
        print(f"Error obteniendo valoración del usuario: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<character_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite_character(character_id):
    """Agregar o quitar personaje de favoritos"""
    try:
        character_oid = sirope.OID.from_text(character_id)
        character = current_app.sirope.load(character_oid)
        
        if not character:
            return jsonify({'success': False, 'message': 'Personaje no encontrado'})
        
        # Toggle favorite status
        is_favorite = current_user.toggle_favorite(character_oid)
        
        # Update character favorite count if the model supports it
        if hasattr(character, 'favorite_count'):
            if is_favorite:
                character.favorite_count = getattr(character, 'favorite_count', 0) + 1
            else:
                character.favorite_count = max(0, getattr(character, 'favorite_count', 1) - 1)
            current_app.sirope.save(character)
        
        current_app.sirope.save(current_user)
        
        message = 'Agregado a favoritos' if is_favorite else 'Removido de favoritos'
        
        return jsonify({
            'success': True,
            'is_favorite': is_favorite,
            'message': message
        })
        
    except Exception as e:
        print(f"Error en favoritos: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<character_id>/favorite-status', methods=['GET'])
@login_required
def get_favorite_status(character_id):
    """Obtener estado de favorito del personaje"""
    try:
        character_oid = sirope.OID.from_text(character_id)
        is_favorite = current_user.is_favorite(character_oid)
        
        return jsonify({
            'success': True,
            'is_favorite': is_favorite
        })
        
    except Exception as e:
        print(f"Error obteniendo estado de favorito: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<character_id>/view', methods=['POST'])
def increment_view(character_id):
    """Incrementar contador de visualizaciones"""
    try:
        character_oid = sirope.OID.from_text(character_id)
        character = current_app.sirope.load(character_oid)
        
        if not character:
            return jsonify({'success': False, 'message': 'Personaje no encontrado'})
        
        # Increment view count if the model supports it
        if hasattr(character, 'view_count'):
            character.view_count = getattr(character, 'view_count', 0) + 1
        else:
            character.view_count = 1
            
        current_app.sirope.save(character)
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error incrementando visualización: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})