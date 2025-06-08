from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sirope
from controllers.house_controller import HouseController
from controllers.character_controller import CharacterController

house_bp = Blueprint('houses', __name__, url_prefix='/houses')
srp = sirope.Sirope()
house_controller = HouseController(srp)
character_controller = CharacterController(srp)

@house_bp.route('/')
def house_list():
    houses = house_controller.get_all_houses()
    return render_template('houses/list.html', houses=houses)

@house_bp.route('/<house_id>')
def house_detail(house_id):
    house = house_controller.get_house_by_id(house_id)
    if not house:
        flash('Casa no encontrada', 'danger')
        return redirect(url_for('houses.house_list'))
    
    # Obtener información de los miembros de la casa
    members = []
    for character_id in house.members:
        character = character_controller.get_character_by_id(character_id)
        if character:
            members.append(character)
    
    return render_template('houses/detail.html', house=house, members=members)

@house_bp.route('/create', methods=['GET', 'POST'])
@login_required
def house_create():
    if request.method == 'POST':
        name = request.form.get('name')
        sigil = request.form.get('sigil')
        words = request.form.get('words')
        region = request.form.get('region')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        
        if not name or not sigil or not description:
            flash('Los campos nombre, emblema y descripción son obligatorios', 'danger')
            return render_template('houses/create.html')
        
        try:
            house = house_controller.create_house(name, sigil, words, region, description, image_url)
            flash('Casa creada correctamente', 'success')
            # Redirigir a la lista de casas en lugar del detalle
            return redirect(url_for('houses.house_list'))
        except Exception as e:
            flash(f'Error al crear la casa: {str(e)}', 'danger')
            return render_template('houses/create.html')
    
    return render_template('houses/create.html')

@house_bp.route('/edit/<house_id>', methods=['GET', 'POST'])
@login_required
def house_edit(house_id):
    house = house_controller.get_house_by_id(house_id)
    if not house:
        flash('Casa no encontrada', 'danger')
        return redirect(url_for('houses.house_list'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        sigil = request.form.get('sigil')
        words = request.form.get('words')
        region = request.form.get('region')
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        
        if not name or not sigil or not description:
            flash('Los campos nombre, emblema y descripción son obligatorios', 'danger')
            return render_template('houses/edit.html', house=house)
        
        success, message = house_controller.update_house(
            house_id, name, sigil, words, region, description, image_url
        )
        
        if success:
            flash(message, 'success')
            return redirect(url_for('houses.house_detail', house_id=house_id))
        else:
            flash(message, 'danger')
    
    return render_template('houses/edit.html', house=house)

@house_bp.route('/delete/<house_id>', methods=['POST'])
@login_required
def house_delete(house_id):
    house = house_controller.get_house_by_id(house_id)
    if not house:
        flash('Casa no encontrada', 'danger')
        return redirect(url_for('houses.house_list'))
    
    # Actualizar los personajes que pertenecen a esta casa
    for character_id in house.members:
        character = character_controller.get_character_by_id(character_id)
        if character:
            character._house_oid = None
            srp.save(character)
    
    success, message = house_controller.delete_house(house_id)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    
    return redirect(url_for('houses.house_list'))