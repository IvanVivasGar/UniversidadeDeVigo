from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import sirope
from controllers.event_controller import EventController
from controllers.character_controller import CharacterController
from controllers.house_controller import HouseController

event_bp = Blueprint('events', __name__, url_prefix='/events')
srp = sirope.Sirope()
event_controller = EventController(srp)
character_controller = CharacterController(srp)
house_controller = HouseController(srp)

@event_bp.route('/')
def event_list():
    try:
        events = event_controller.get_all_events()
        # Inicializar atributos para eventos que podrían no tenerlos
        for event in events:
            if not hasattr(event, '_related_characters') or event._related_characters is None:
                event._related_characters = []
            if not hasattr(event, '_related_houses') or event._related_houses is None:
                event._related_houses = []
            if not hasattr(event, '_comments') or event._comments is None:
                event._comments = []
        return render_template('events/list.html', events=events)
    except Exception as e:
        flash(f'Error al cargar los eventos: {str(e)}', 'danger')
        return render_template('events/list.html', events=[])

@event_bp.route('/<event_id>')
def event_detail(event_id):
    event = event_controller.get_event_by_id(event_id)
    if not event:
        flash('Evento no encontrado', 'danger')
        return redirect(url_for('events.event_list'))
    
    # Obtener información de personajes y casas relacionadas
    related_characters = []
    for character_id in event.related_characters:
        character = character_controller.get_character_by_id(character_id)
        if character:
            related_characters.append(character)
    
    related_houses = []
    for house_id in event.related_houses:
        house = house_controller.get_house_by_id(house_id)
        if house:
            related_houses.append(house)
    
    return render_template('events/detail.html', 
                          event=event, 
                          related_characters=related_characters,
                          related_houses=related_houses)

@event_bp.route('/create', methods=['GET', 'POST'])
@login_required
def event_create():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            season = int(request.form.get('season', 0))
            episode = int(request.form.get('episode', 0))
            description = request.form.get('description')
            location = request.form.get('location')
            importance = int(request.form.get('importance', 0))
            image_url = request.form.get('image_url')
            
            if not name or not description or not location or season <= 0 or episode <= 0 or not 1 <= importance <= 5:
                flash('Todos los campos son obligatorios y la importancia debe estar entre 1 y 5', 'danger')
                characters = character_controller.get_all_characters()
                houses = house_controller.get_all_houses()
                return render_template('events/create.html', characters=characters, houses=houses)
            
            event = event_controller.create_event(name, season, episode, description, location, importance, image_url)
            
            # Añadir personajes relacionados
            if event._oid:
                related_character_ids = request.form.getlist('related_characters')
                for character_id in related_character_ids:
                    try:
                        event_controller.add_related_character(event._oid, character_id)
                    except Exception as e:
                        # Registrar el error pero continuar con el proceso
                        print(f"Error al relacionar personaje {character_id}: {str(e)}")
                
                # Añadir casas relacionadas
                related_house_ids = request.form.getlist('related_houses')
                for house_id in related_house_ids:
                    try:
                        event_controller.add_related_house(event._oid, house_id)
                    except Exception as e:
                        # Registrar el error pero continuar con el proceso
                        print(f"Error al relacionar casa {house_id}: {str(e)}")
            
            flash('Evento creado correctamente', 'success')
            # Redirigir a la lista de eventos en vez de la página de detalle
            return redirect(url_for('events.event_list'))
            
        except Exception as e:
            flash(f'Error al crear el evento: {str(e)}', 'danger')
            characters = character_controller.get_all_characters()
            houses = house_controller.get_all_houses()
            return render_template('events/create.html', characters=characters, houses=houses)
    
    characters = character_controller.get_all_characters()
    houses = house_controller.get_all_houses()
    return render_template('events/create.html', characters=characters, houses=houses)

@event_bp.route('/edit/<event_id>', methods=['GET', 'POST'])
@login_required
def event_edit(event_id):
    event = event_controller.get_event_by_id(event_id)
    if not event:
        flash('Evento no encontrado', 'danger')
        return redirect(url_for('events.event_list'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        season = int(request.form.get('season', 0))
        episode = int(request.form.get('episode', 0))
        description = request.form.get('description')
        location = request.form.get('location')
        importance = int(request.form.get('importance', 0))
        image_url = request.form.get('image_url')
        
        if not name or not description or not location or season <= 0 or episode <= 0 or not 1 <= importance <= 5:
            flash('Todos los campos son obligatorios y la importancia debe estar entre 1 y 5', 'danger')
            characters = character_controller.get_all_characters()
            houses = house_controller.get_all_houses()
            return render_template('events/edit.html', 
                                  event=event,
                                  characters=characters, 
                                  houses=houses)
        
        success, message = event_controller.update_event(
            event_id, name, season, episode, description, location, importance, image_url
        )
        
        # Actualizar personajes relacionados
        # Primero limpiar las relaciones actuales
        new_related_character_ids = set(request.form.getlist('related_characters'))
        current_related_character_ids = set(event.related_characters)
        
        # Eliminar los personajes que ya no están relacionados
        for character_id in current_related_character_ids - new_related_character_ids:
            event_controller.remove_related_character(event_id, character_id)
        
        # Añadir los nuevos personajes relacionados
        for character_id in new_related_character_ids - current_related_character_ids:
            event_controller.add_related_character(event_id, character_id)
        
        # Actualizar casas relacionadas de manera similar
        new_related_house_ids = set(request.form.getlist('related_houses'))
        current_related_house_ids = set(event.related_houses)
        
        for house_id in current_related_house_ids - new_related_house_ids:
            event_controller.remove_related_house(event_id, house_id)
        
        for house_id in new_related_house_ids - current_related_house_ids:
            event_controller.add_related_house(event_id, house_id)
        
        if success:
            flash(message, 'success')
            return redirect(url_for('events.event_detail', event_id=event_id))
        else:
            flash(message, 'danger')
    
    characters = character_controller.get_all_characters()
    houses = house_controller.get_all_houses()
    return render_template('events/edit.html', 
                          event=event,
                          characters=characters, 
                          houses=houses)

@event_bp.route('/delete/<event_id>', methods=['POST'])
@login_required
def event_delete(event_id):
    success, message = event_controller.delete_event(event_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('events.event_list'))

@event_bp.route('/add_comment/<event_id>', methods=['POST'])
@login_required
def event_add_comment(event_id):
    text = request.form.get('comment', '').strip()
    if not text:
        if request.is_xhr:
            return jsonify(success=False, message="El comentario no puede estar vacío")
        flash('El comentario no puede estar vacío', 'danger')
        return redirect(url_for('events.event_detail', event_id=event_id))
    
    success, message = event_controller.add_comment(event_id, current_user.get_id(), text)
    
    if request.is_xhr:
        return jsonify(success=success, message=message)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('events.event_detail', event_id=event_id))