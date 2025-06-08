from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app.models.event import Event
from app.models.character import Character
from app.models.house import House
from app.utils.helpers import get_entity_by_name, search_entities, save_uploaded_file
import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

bp = Blueprint('events', __name__)

@bp.route('/')
def events():
    """Página principal de eventos con búsqueda y filtro por temporada"""
    search_term = request.args.get('search', '')
    season_filter = request.args.get('season', '')
    
    try:
        # Búsqueda básica
        events_list = search_entities(current_app.sirope, Event, search_term)
        
        # Filtro por temporada
        if season_filter:
            try:
                season_num = int(season_filter)
                events_list = [e for e in events_list if e.season == season_num]
            except ValueError:
                pass
        
        # Obtener todas las temporadas disponibles para el filtro
        all_events = list(current_app.sirope.load_all(Event))
        available_seasons = sorted(list(set(e.season for e in all_events)))
        
        return render_template('events/events.html', 
                             events=events_list, 
                             search_term=search_term,
                             season_filter=season_filter,
                             available_seasons=available_seasons)
    except Exception as e:
        print(f"Error cargando eventos: {e}")
        return render_template('events/events.html', 
                             events=[], 
                             search_term=search_term,
                             season_filter=season_filter,
                             available_seasons=[])

@bp.route('/<event_id>')
def event_detail(event_id):
    """Página de detalle de un evento"""
    try:
        event_oid = sirope.OID.from_text(event_id)
        event = current_app.sirope.load(event_oid)
        
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('events.events'))
        
        # Obtener personajes involucrados
        characters = []
        if hasattr(event, 'characters_involved') and event.characters_involved:
            for character_oid in event.characters_involved:
                try:
                    # Asegurar que el OID es válido antes de cargar
                    if character_oid and hasattr(character_oid, '__class__'):
                        character = current_app.sirope.load(character_oid)
                        if character:
                            characters.append(character)
                except Exception as char_error:
                    print(f"Error cargando personaje {character_oid}: {char_error}")
                    continue
        
        # Obtener casas involucradas
        houses = []
        if hasattr(event, 'houses_involved') and event.houses_involved:
            for house_oid in event.houses_involved:
                try:
                    # Asegurar que el OID es válido antes de cargar
                    if house_oid and hasattr(house_oid, '__class__'):
                        house = current_app.sirope.load(house_oid)
                        if house:
                            houses.append(house)
                except Exception as house_error:
                    print(f"Error cargando casa {house_oid}: {house_error}")
                    continue
        
        return render_template('events/event_detail.html', 
                             event=event, 
                             characters=characters,
                             houses=houses)
                             
    except Exception as e:
        print(f"Error cargando detalle del evento: {e}")
        flash('Error cargando el evento', 'error')
        return redirect(url_for('events.events'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Crear nuevo evento"""
    if request.method == 'POST':
        # Detectar si es una petición AJAX
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        try:
            # Procesar datos del formulario
            event_data = process_event_form_data(request.form, request.files)
            
            if not event_data:
                error_msg = 'Error procesando los datos del formulario'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('events.create_event'))
            
            # Validar datos
            validation_errors = validate_event_data(event_data)
            if validation_errors:
                error_msg = 'Errores de validación: ' + ', '.join(validation_errors)
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg, 'errors': validation_errors})
                flash(error_msg, 'error')
                return redirect(url_for('events.create_event'))
            
            # Verificar que el evento no exista
            existing_event = get_entity_by_name(current_app.sirope, Event, event_data['name'])
            if existing_event:
                error_msg = 'Ya existe un evento con ese nombre'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash(error_msg, 'error')
                return redirect(url_for('events.create_event'))
            
            # Crear evento
            event = Event(
                event_data['name'], 
                event_data['season'], 
                event_data['episode'], 
                event_data['description'], 
                event_data['image_urls']
            )
            
            # Establecer rating de importancia
            if event_data['importance_rating']:
                event.set_importance_rating(event_data['importance_rating'])
            
            # Agregar personajes involucrados
            for char_oid in event_data['character_oids']:
                event.add_character(char_oid)
            
            # Agregar casas involucradas
            for house_oid in event_data['house_oids']:
                event.add_house(house_oid)
                # También agregar el evento a la casa
                try:
                    house = current_app.sirope.load(house_oid)
                    if house:
                        house.add_event(event.__oid__)
                        current_app.sirope.save(house)
                except:
                    pass
            
            # Establecer el creador
            if hasattr(event, 'created_by'):
                event.created_by = current_user.__oid__
            
            oid = current_app.sirope.save(event)
            
            success_msg = 'Evento creado exitosamente'
            if is_ajax:
                return jsonify({
                    'success': True, 
                    'message': success_msg,
                    'redirect_url': url_for('events.event_detail', event_id=str(oid))
                })
            
            flash(success_msg, 'success')
            return redirect(url_for('events.event_detail', event_id=str(oid)))
            
        except Exception as e:
            print(f"Error creando evento: {e}")
            error_msg = f'Error creando el evento: {str(e)}'
            if is_ajax:
                return jsonify({'success': False, 'message': error_msg})
            flash('Error creando el evento', 'error')
            return redirect(url_for('events.create_event'))
    
    # GET request - mostrar formulario
    try:
        characters = list(current_app.sirope.load_all(Character))
        houses = list(current_app.sirope.load_all(House))
    except:
        characters = []
        houses = []
    
    return render_template('events/event_form.html', 
                         characters=characters, 
                         houses=houses)

@bp.route('/<event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Editar evento existente"""
    try:
        event_oid = sirope.OID.from_text(event_id)
        event = current_app.sirope.load(event_oid)
        
        if not event:
            flash('Evento no encontrado', 'error')
            return redirect(url_for('events.events'))
        
        if request.method == 'POST':
            # Detectar si es una petición AJAX
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            try:
                # Procesar datos del formulario
                event_data = process_event_form_data(request.form, request.files)
                
                if not event_data:
                    error_msg = 'Error procesando los datos del formulario'
                    if is_ajax:
                        return jsonify({'success': False, 'message': error_msg})
                    flash(error_msg, 'error')
                    return redirect(url_for('events.edit_event', event_id=event_id))
                
                # Validar datos
                validation_errors = validate_event_data(event_data)
                if validation_errors:
                    error_msg = 'Errores de validación: ' + ', '.join(validation_errors)
                    if is_ajax:
                        return jsonify({'success': False, 'message': error_msg, 'errors': validation_errors})
                    flash(error_msg, 'error')
                    return redirect(url_for('events.edit_event', event_id=event_id))
                
                # Verificar nombre único (excepto el actual)
                existing_event = get_entity_by_name(current_app.sirope, Event, event_data['name'])
                if existing_event and existing_event.__oid__ != event_oid:
                    error_msg = 'Ya existe un evento con ese nombre'
                    if is_ajax:
                        return jsonify({'success': False, 'message': error_msg})
                    flash(error_msg, 'error')
                    return redirect(url_for('events.edit_event', event_id=event_id))
                
                # Actualizar datos básicos
                event.name = event_data['name']
                event.season = event_data['season']
                event.episode = event_data['episode']
                event.description = event_data['description']
                
                # Actualizar rating de importancia
                if event_data['importance_rating']:
                    event.set_importance_rating(event_data['importance_rating'])
                
                # Agregar nuevas imágenes
                for image_url in event_data['image_urls']:
                    event.add_image(image_url)
                
                # Actualizar personajes involucrados
                event.characters_involved = []
                for char_oid in event_data['character_oids']:
                    event.add_character(char_oid)
                
                # Actualizar casas involucradas
                event.houses_involved = []
                for house_oid in event_data['house_oids']:
                    event.add_house(house_oid)
                    # También agregar el evento a la casa
                    try:
                        house = current_app.sirope.load(house_oid)
                        if house:
                            house.add_event(event_oid)
                            current_app.sirope.save(house)
                    except:
                        pass
                
                current_app.sirope.save(event)
                
                success_msg = 'Evento actualizado exitosamente'
                if is_ajax:
                    return jsonify({
                        'success': True, 
                        'message': success_msg,
                        'redirect_url': url_for('events.event_detail', event_id=event_id)
                    })
                
                flash(success_msg, 'success')
                return redirect(url_for('events.event_detail', event_id=event_id))
                
            except Exception as e:
                print(f"Error actualizando evento: {e}")
                error_msg = f'Error actualizando el evento: {str(e)}'
                if is_ajax:
                    return jsonify({'success': False, 'message': error_msg})
                flash('Error actualizando el evento', 'error')
                return redirect(url_for('events.edit_event', event_id=event_id))
        
        # GET request - mostrar formulario de edición
        try:
            characters = list(current_app.sirope.load_all(Character))
            houses = list(current_app.sirope.load_all(House))
        except:
            characters = []
            houses = []
        
        return render_template('events/event_form.html', 
                             event=event,
                             characters=characters, 
                             houses=houses,
                             editing=True)
                             
    except Exception as e:
        print(f"Error editando evento: {e}")
        flash('Error cargando el evento', 'error')
        return redirect(url_for('events.events'))

@bp.route('/<event_id>/rate', methods=['POST'])
@login_required
def rate_event(event_id):
    """Calificar o actualizar calificación de un evento"""
    try:
        data = request.get_json()
        rating = int(data.get('rating', 0))
        
        if not (1 <= rating <= 5):
            return jsonify({'success': False, 'message': 'Rating debe estar entre 1 y 5'})
        
        event_oid = sirope.OID.from_text(event_id)
        event = current_app.sirope.load(event_oid)
        
        if not event:
            return jsonify({'success': False, 'message': 'Evento no encontrado'})
        
        # Obtener rating anterior del usuario
        previous_rating = event.get_user_rating(current_user.__oid__)
        
        # Agregar o actualizar calificación
        success = event.add_user_rating(current_user.__oid__, rating)
        
        if success:
            current_app.sirope.save(event)
            
            action = "actualizada" if previous_rating > 0 else "agregada"
            message = f'Calificación {action} exitosamente'
            
            return jsonify({
                'success': True, 
                'message': message,
                'user_rating': rating,
                'average_rating': event.get_average_rating(),
                'rating_count': event.get_rating_count(),
                'previous_rating': previous_rating
            })
        else:
            return jsonify({'success': False, 'message': 'Error procesando la calificación'})
        
    except Exception as e:
        print(f"Error calificando evento: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/<event_id>/remove-rating', methods=['POST'])
@login_required
def remove_rating(event_id):
    """Remover calificación de un evento"""
    try:
        event_oid = sirope.OID.from_text(event_id)
        event = current_app.sirope.load(event_oid)
        
        if not event:
            return jsonify({'success': False, 'message': 'Evento no encontrado'})
        
        # Remover calificación del usuario
        success = event.remove_user_rating(current_user.__oid__)
        
        if success:
            current_app.sirope.save(event)
            
            return jsonify({
                'success': True, 
                'message': 'Calificación removida exitosamente',
                'average_rating': event.get_average_rating(),
                'rating_count': event.get_rating_count()
            })
        else:
            return jsonify({'success': False, 'message': 'No tienes calificación para este evento'})
        
    except Exception as e:
        print(f"Error removiendo calificación: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

# ========================================================================
# API ENDPOINTS PARA JAVASCRIPT
# ========================================================================

@bp.route('/api/check-name')
def api_check_event_name():
    """API para verificar disponibilidad de nombre de evento"""
    name = request.args.get('name', '').strip()
    
    if not name:
        return jsonify({'exists': False})
    
    try:
        existing_event = get_entity_by_name(current_app.sirope, Event, name)
        return jsonify({'exists': existing_event is not None})
    except Exception as e:
        print(f"Error verificando nombre de evento: {e}")
        return jsonify({'exists': False, 'error': str(e)})

@bp.route('/api/episodes/<int:season>')
def api_get_episodes_by_season(season):
    """API para obtener episodios válidos por temporada"""
    # Episodios por temporada según Game of Thrones
    episodes_by_season = {
        1: 10, 2: 10, 3: 10, 4: 10, 5: 10, 6: 10, 7: 7, 8: 6
    }
    
    max_episodes = episodes_by_season.get(season, 10)
    episodes = [{'value': i, 'label': f'Episodio {i}'} for i in range(1, max_episodes + 1)]
    
    return jsonify({'episodes': episodes, 'max_episodes': max_episodes})

@bp.route('/api/characters/search')
def api_search_characters():
    """API para búsqueda de personajes en tiempo real"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 20))
    
    try:
        if not query:
            characters = list(current_app.sirope.load_all(Character))[:limit]
        else:
            characters = search_entities(current_app.sirope, Character, query)[:limit]
        
        results = []
        for char in characters:
            results.append({
                'id': str(char.__oid__),
                'name': char.name,
                'house': getattr(char, 'house_name', 'Sin casa'),
                'status': getattr(char, 'status', 'Desconocido')
            })
        
        return jsonify({'characters': results})
        
    except Exception as e:
        print(f"Error buscando personajes: {e}")
        return jsonify({'characters': [], 'error': str(e)})

@bp.route('/api/houses/search')
def api_search_houses():
    """API para búsqueda de casas en tiempo real"""
    query = request.args.get('q', '').strip()
    limit = int(request.args.get('limit', 20))
    
    try:
        if not query:
            houses = list(current_app.sirope.load_all(House))[:limit]
        else:
            houses = search_entities(current_app.sirope, House, query)[:limit]
        
        results = []
        for house in houses:
            results.append({
                'id': str(house.__oid__),
                'name': house.name,
                'region': getattr(house, 'region', 'Región desconocida'),
                'words': getattr(house, 'words', '')
            })
        
        return jsonify({'houses': results})
        
    except Exception as e:
        print(f"Error buscando casas: {e}")
        return jsonify({'houses': [], 'error': str(e)})

@bp.route('/api/upload-image', methods=['POST'])
@login_required
def api_upload_image():
    """API para subida de imágenes vía AJAX"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No se encontró archivo'})
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No se seleccionó archivo'})
        
        # Validar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and 
                file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Formato de archivo no válido'})
        
        # Validar tamaño (5MB máximo)
        file.seek(0, 2)  # Ir al final del archivo
        size = file.tell()
        file.seek(0)  # Volver al inicio
        
        if size > 5 * 1024 * 1024:
            return jsonify({'success': False, 'message': 'El archivo supera los 5MB'})
        
        # Guardar archivo
        image_url = save_uploaded_file(file, 'events')
        if image_url:
            return jsonify({
                'success': True, 
                'image_url': image_url,
                'message': 'Imagen subida exitosamente'
            })
        else:
            return jsonify({'success': False, 'message': 'Error guardando el archivo'})
        
    except Exception as e:
        print(f"Error subiendo imagen: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/api/validate-form', methods=['POST'])
@login_required
def api_validate_event_form():
    """API para validación completa del formulario"""
    try:
        data = request.get_json()
        errors = []
        warnings = []
        
        # Validar nombre
        name = data.get('name', '').strip()
        if not name:
            errors.append('El nombre es requerido')
        elif len(name) < 3:
            errors.append('El nombre debe tener al menos 3 caracteres')
        elif len(name) > 100:
            errors.append('El nombre no puede superar los 100 caracteres')
        else:
            # Verificar disponibilidad
            existing_event = get_entity_by_name(current_app.sirope, Event, name)
            if existing_event:
                event_id = data.get('event_id')  # Para modo edición
                if not event_id or str(existing_event.__oid__) != event_id:
                    errors.append('Ya existe un evento con ese nombre')
        
        # Validar temporada
        season = data.get('season')
        if not season:
            errors.append('La temporada es requerida')
        else:
            try:
                season_num = int(season)
                if not (1 <= season_num <= 8):
                    errors.append('La temporada debe estar entre 1 y 8')
            except ValueError:
                errors.append('Temporada inválida')
        
        # Validar episodio
        episode = data.get('episode')
        if not episode:
            errors.append('El episodio es requerido')
        else:
            try:
                episode_num = int(episode)
                if episode_num < 1:
                    errors.append('El episodio debe ser mayor a 0')
            except ValueError:
                errors.append('Episodio inválido')
        
        # Validar descripción
        description = data.get('description', '').strip()
        if not description:
            errors.append('La descripción es requerida')
        elif len(description) < 50:
            errors.append('La descripción debe tener al menos 50 caracteres')
        elif len(description) > 2000:
            errors.append('La descripción no puede superar los 2000 caracteres')
        
        # Validar rating de importancia
        importance_rating = data.get('importance_rating')
        if not importance_rating:
            warnings.append('Se recomienda establecer un rating de importancia')
        else:
            try:
                rating_num = int(importance_rating)
                if not (1 <= rating_num <= 5):
                    errors.append('El rating debe estar entre 1 y 5')
            except ValueError:
                errors.append('Rating inválido')
        
        # Validaciones adicionales
        characters = data.get('character_ids', [])
        if len(characters) > 10:
            warnings.append('Muchos personajes involucrados. Considera si todos son relevantes.')
        
        houses = data.get('house_ids', [])
        if len(houses) > 5:
            warnings.append('Muchas casas involucradas. Considera si todas son relevantes.')
        
        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'message': 'Validación completada'
        })
        
    except Exception as e:
        print(f"Error validando formulario: {e}")
        return jsonify({
            'valid': False,
            'errors': ['Error de validación en el servidor'],
            'warnings': [],
            'message': str(e)
        })

@bp.route('/api/stats')
def api_event_stats():
    """API para estadísticas de eventos"""
    try:
        events = list(current_app.sirope.load_all(Event))
        
        # Estadísticas básicas
        total_events = len(events)
        events_by_season = {}
        avg_ratings = []
        
        for event in events:
            # Contar por temporada
            season = getattr(event, 'season', 0)
            events_by_season[season] = events_by_season.get(season, 0) + 1
            
            # Ratings promedio
            if hasattr(event, 'ratings') and event.ratings:
                avg_rating = sum(event.ratings) / len(event.ratings)
                avg_ratings.append(avg_rating)
        
        overall_avg_rating = sum(avg_ratings) / len(avg_ratings) if avg_ratings else 0
        
        return jsonify({
            'total_events': total_events,
            'events_by_season': events_by_season,
            'average_rating': round(overall_avg_rating, 2),
            'seasons': list(range(1, 9))
        })
        
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        return jsonify({
            'total_events': 0,
            'events_by_season': {},
            'average_rating': 0,
            'seasons': list(range(1, 9))
        })

# ========================================================================
# FUNCIONES AUXILIARES
# ========================================================================

def process_event_form_data(form_data, files):
    """Procesar datos del formulario de eventos"""
    try:
        # Extraer datos básicos
        event_data = {
            'name': form_data.get('name', '').strip(),
            'season': int(form_data.get('season', 0)),
            'episode': int(form_data.get('episode', 0)),
            'description': form_data.get('description', '').strip(),
            'importance_rating': int(form_data.get('importance_rating', 0)) if form_data.get('importance_rating') else None
        }
        
        # Procesar personajes
        character_ids = form_data.getlist('character_ids')
        event_data['character_oids'] = []
        for char_id in character_ids:
            try:
                char_oid = sirope.OID.from_text(char_id)
                event_data['character_oids'].append(char_oid)
            except:
                pass
        
        # Procesar casas
        house_ids = form_data.getlist('house_ids')
        event_data['house_oids'] = []
        for house_id in house_ids:
            try:
                house_oid = sirope.OID.from_text(house_id)
                event_data['house_oids'].append(house_oid)
            except:
                pass
        
        # Procesar imágenes
        image_urls = []
        
        # Imagen principal
        if 'image' in files:
            main_file = files['image']
            if main_file.filename != '':
                main_url = save_uploaded_file(main_file, 'events')
                if main_url:
                    image_urls.append(main_url)
        
        # Imágenes adicionales
        if 'additional_images' in files:
            additional_files = files.getlist('additional_images')
            for file in additional_files[:4]:  # Máximo 4 adicionales
                if file.filename != '':
                    url = save_uploaded_file(file, 'events')
                    if url:
                        image_urls.append(url)
        
        event_data['image_urls'] = image_urls
        
        return event_data
        
    except Exception as e:
        print(f"Error procesando datos del formulario: {e}")
        return None

def validate_event_data(event_data):
    """Validar datos de evento"""
    errors = []
    
    if not event_data['name']:
        errors.append('El nombre es requerido')
    elif len(event_data['name']) < 3:
        errors.append('El nombre debe tener al menos 3 caracteres')
    
    if not (1 <= event_data['season'] <= 8):
        errors.append('La temporada debe estar entre 1 y 8')
    
    if event_data['episode'] < 1:
        errors.append('El episodio debe ser mayor a 0')
    
    if not event_data['description']:
        errors.append('La descripción es requerida')
    elif len(event_data['description']) < 50:
        errors.append('La descripción debe tener al menos 50 caracteres')
    
    return errors