from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.models.character import Character
from app.models.house import House
from app.utils.helpers import get_entity_by_name
import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

bp = Blueprint('api', __name__)

@bp.route('/characters', methods=['GET'])
def api_characters():
    """API endpoint para obtener todos los personajes"""
    try:
        characters_list = list(current_app.sirope.load_all(Character))
        
        # Convert characters to JSON-serializable format
        characters_data = []
        for character in characters_list:
            # Obtener el nombre real de la casa si está afiliado
            house_name = None
            if hasattr(character, 'house_affiliation') and character.house_affiliation:
                try:
                    house = current_app.sirope.load(character.house_affiliation)
                    if house:
                        house_name = house.name
                except:
                    house_name = None
            
            character_data = {
                'id': str(character.__oid__),
                'name': character.name,
                'status': character.status,
                'description': character.description,
                'image_url': character.image_url,
                'average_rating': character.get_average_rating(),
                'rating_count': character.rating_count,
                'house': house_name,  # Enviar el nombre real de la casa o None
                'view_count': getattr(character, 'view_count', 0),
                'favorite_count': getattr(character, 'favorite_count', 0)
            }
            characters_data.append(character_data)
        
        return jsonify(characters_data)
        
    except Exception as e:
        print(f"Error en API de personajes: {e}")
        return jsonify({'error': 'Error cargando personajes'}), 500

@bp.route('/characters/check-name', methods=['GET'])
def check_character_name():
    """API endpoint para verificar si un nombre de personaje ya existe"""
    try:
        name = request.args.get('name', '').strip()
        if not name:
            return jsonify({'exists': False})
        
        existing_character = get_entity_by_name(current_app.sirope, Character, name)
        return jsonify({'exists': existing_character is not None})
        
    except Exception as e:
        print(f"Error verificando nombre: {e}")
        return jsonify({'error': 'Error verificando nombre'}), 500

@bp.route('/characters/<character_id>/favorite', methods=['POST'])
@login_required
def api_toggle_favorite_character(character_id):
    """API endpoint para agregar o quitar personaje de favoritos"""
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
        print(f"Error en favoritos API: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})

@bp.route('/houses', methods=['GET'])
def api_houses():
    """API endpoint para obtener todas las casas"""
    try:
        houses_list = list(current_app.sirope.load_all(House))
        
        # Convert houses to JSON-serializable format
        houses_data = []
        for house in houses_list:
            # Obtener imagen principal (primera imagen o URL por defecto)
            image_url = ''
            if hasattr(house, 'images') and house.images:
                image_url = house.images[0]
            elif hasattr(house, 'image_urls') and house.image_urls:
                # Compatibilidad con casas antiguas
                image_url = house.image_urls[0]
            
            house_data = {
                'id': str(house.__oid__),
                'name': house.name,
                'motto': getattr(house, 'motto', ''),
                'region': getattr(house, 'region', ''),
                'status': getattr(house, 'status', 'mayor'),
                'description': getattr(house, 'description', ''),
                'sigil_url': image_url,
                'image_url': image_url,  # Alias para compatibilidad
                'member_count': len(getattr(house, 'members', [])),
                'average_rating': house.get_average_rating() if hasattr(house, 'get_average_rating') else 0.0,
                'rating_count': getattr(house, 'rating_count', 0),
                'created_at': getattr(house, 'created_at', '').isoformat() if hasattr(getattr(house, 'created_at', None), 'isoformat') else '',
                'view_count': getattr(house, 'view_count', 0),
                'favorite_count': getattr(house, 'favorite_count', 0)
            }
            houses_data.append(house_data)
        
        return jsonify(houses_data)
        
    except Exception as e:
        print(f"Error en API de casas: {e}")
        return jsonify({'error': 'Error cargando casas'}), 500

@bp.route('/search', methods=['GET'])
def api_search():
    """API endpoint para búsqueda general"""
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'all')  # 'all', 'characters', 'houses'
        
        results = {
            'characters': [],
            'houses': [],
            'total': 0
        }
        
        if not query:
            return jsonify(results)
        
        # Search characters
        if search_type in ['all', 'characters']:
            try:
                characters = list(current_app.sirope.load_all(Character))
                for character in characters:
                    if (query.lower() in character.name.lower() or 
                        query.lower() in character.description.lower()):
                        results['characters'].append({
                            'id': str(character.__oid__),
                            'name': character.name,
                            'status': character.status,
                            'type': 'character'
                        })
            except:
                pass
        
        # Search houses
        if search_type in ['all', 'houses']:
            try:
                houses = list(current_app.sirope.load_all(House))
                for house in houses:
                    if (query.lower() in house.name.lower() or 
                        query.lower() in getattr(house, 'description', '').lower()):
                        results['houses'].append({
                            'id': str(house.__oid__),
                            'name': house.name,
                            'region': getattr(house, 'region', ''),
                            'type': 'house'
                        })
            except:
                pass
        
        results['total'] = len(results['characters']) + len(results['houses'])
        
        return jsonify(results)
        
    except Exception as e:
        print(f"Error en búsqueda API: {e}")
        return jsonify({'error': 'Error en búsqueda'}), 500

@bp.route('/houses/<house_id>/favorite', methods=['POST'])
@login_required
def api_toggle_favorite_house(house_id):
    """API endpoint para agregar o quitar casa de favoritos"""
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
        print(f"Error en favoritos de casas API: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'})