from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import sirope
from controllers.character_controller import CharacterController
from controllers.house_controller import HouseController
from sirope.oid import OID
import math

# Clase auxiliar para paginación
class Pagination:
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
        self.start_index = (page - 1) * per_page + 1
        self.end_index = min(page * per_page, total_count)
    
    @property
    def items(self):
        return self.total_count
    
    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None
    
    @property
    def has_prev(self):
        return self.page > 1
    
    @property
    def has_next(self):
        return self.page < self.pages
    
    @property
    def pages(self):
        return math.ceil(self.total_count / self.per_page)
    
    @property
    def total(self):
        return self.total_count
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        last = self.pages
        for num in range(1, last + 1):
            if num <= left_edge or \
               (self.page - left_current - 1 < num < self.page + right_current) or \
               num > last - right_edge:
                yield num

character_bp = Blueprint('characters', __name__, url_prefix='/characters')
srp = sirope.Sirope()
character_controller = CharacterController(srp)
house_controller = HouseController(srp)

@character_bp.route('/')
def character_list():
    page = request.args.get('page', 1, type=int)
    per_page = 12  # 12 personajes por página
    
    # Obtener todos los personajes
    all_characters = character_controller.get_all_characters()
    total_count = len(all_characters)
    
    # Calcular paginación
    start = (page - 1) * per_page
    end = start + per_page
    characters = all_characters[start:end]
    
    # Crear objeto de paginación solo si hay más de 12 personajes
    pagination = None
    if total_count > per_page:
        pagination = Pagination(page, per_page, total_count)
    
    return render_template('characters/list.html', characters=characters, pagination=pagination)

@character_bp.route('/<character_id>')
def character_detail(character_id):
    character = character_controller.get_character_by_id(character_id)
    if not character:
        flash('Personaje no encontrado', 'danger')
        return redirect(url_for('characters.character_list'))
    
    # Obtener información de la casa relacionada
    house = None
    if character.house_oid:
        try:
            house = house_controller.get_house_by_id(character.house_oid)
        except Exception:
            # Si hay un error al cargar la casa, simplemente no se muestra
            pass
    
    return render_template('characters/detail.html', character=character, house=house)

@character_bp.route('/create', methods=['GET', 'POST'])
@login_required
def character_create():
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        house_oid_str = request.form.get('house_oid')
        status = request.form.get('status')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        
        if not name or not status or not description:
            flash('Los campos nombre, estado y descripción son obligatorios', 'danger')
            houses = house_controller.get_all_houses()
            return render_template('characters/create.html', houses=houses)
        
        # Convertir house_oid a OID si es una cadena no vacía
        house_oid = None
        if house_oid_str and house_oid_str.strip():
            try:
                house_oid = OID(house_oid_str)
            except Exception as e:
                flash(f'Error al procesar la casa seleccionada: {str(e)}', 'danger')
                houses = house_controller.get_all_houses()
                return render_template('characters/create.html', houses=houses)
        
        try:
            character = character_controller.create_character(name, title, house_oid, status, description, image_url)
            
            # Si el personaje tiene casa, actualizar la casa con este personaje
            if house_oid and character._oid:
                try:
                    house_controller.add_member_to_house(house_oid, character._oid)
                except Exception as e:
                    flash(f'Personaje creado, pero no se pudo asignar a la casa: {str(e)}', 'warning')
            
            # Mostrar mensaje de éxito y redirigir a la lista de personajes
            # en lugar de intentar redirigir al detalle del personaje
            flash('Personaje creado correctamente', 'success')
            return redirect(url_for('characters.character_list'))
                
        except Exception as e:
            flash(f'Error al crear el personaje: {str(e)}', 'danger')
            houses = house_controller.get_all_houses()
            return render_template('characters/create.html', houses=houses)
    
    houses = house_controller.get_all_houses()
    return render_template('characters/create.html', houses=houses)

@character_bp.route('/edit/<character_id>', methods=['GET', 'POST'])
@login_required
def character_edit(character_id):
    character = character_controller.get_character_by_id(character_id)
    if not character:
        flash('Personaje no encontrado', 'danger')
        return redirect(url_for('characters.character_list'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        title = request.form.get('title')
        new_house_oid_str = request.form.get('house_oid')
        status = request.form.get('status')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        
        if not name or not status or not description:
            flash('Los campos nombre, estado y descripción son obligatorios', 'danger')
            houses = house_controller.get_all_houses()
            return render_template('characters/edit.html', character=character, houses=houses)
        
        # Convertir new_house_oid a OID si es una cadena no vacía
        new_house_oid = None
        if new_house_oid_str and new_house_oid_str.strip():
            try:
                new_house_oid = OID(new_house_oid_str)
            except Exception as e:
                flash(f'Error al procesar la casa seleccionada: {str(e)}', 'danger')
                houses = house_controller.get_all_houses()
                return render_template('characters/edit.html', character=character, houses=houses)
        
        # Si el personaje cambia de casa, actualizar ambas casas
        old_house_oid = character.house_oid
        if old_house_oid != new_house_oid:
            if old_house_oid:
                try:
                    house_controller.remove_member_from_house(old_house_oid, character_id)
                except Exception as e:
                    flash(f'No se pudo eliminar el personaje de la casa anterior: {str(e)}', 'warning')
            
            if new_house_oid:
                try:
                    house_controller.add_member_to_house(new_house_oid, character_id)
                except Exception as e:
                    flash(f'No se pudo asignar el personaje a la nueva casa: {str(e)}', 'warning')
        
        success, message = character_controller.update_character(
            character_id, name, title, new_house_oid, status, description, image_url
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('characters.character_detail', character_id=character_id))
        else:
            flash(message, 'danger')
    
    houses = house_controller.get_all_houses()
    return render_template('characters/edit.html', character=character, houses=houses)

@character_bp.route('/delete/<character_id>', methods=['POST'])
@login_required
def character_delete(character_id):
    character = character_controller.get_character_by_id(character_id)
    if not character:
        flash('Personaje no encontrado', 'danger')
        return redirect(url_for('characters.character_list'))
    
    # Si el personaje tiene casa, eliminar la referencia en la casa
    if character.house_oid:
        house_controller.remove_member_from_house(character.house_oid, character_id)
    
    success, message = character_controller.delete_character(character_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('characters.character_list'))

@character_bp.route('/rate/<character_id>', methods=['POST'])
@login_required
def character_rate(character_id):
    rating = int(request.form.get('rating', 0))
    if not 1 <= rating <= 5:
        if request.is_xhr:
            return jsonify(success=False, message="La valoración debe estar entre 1 y 5")
        flash('La valoración debe estar entre 1 y 5', 'danger')
        return redirect(url_for('characters.character_detail', character_id=character_id))
    
    success, message = character_controller.add_rating(character_id, rating)
    
    if request.is_xhr:
        return jsonify(success=success, message=message)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('characters.character_detail', character_id=character_id))