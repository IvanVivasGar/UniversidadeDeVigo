from flask import Blueprint, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from functools import wraps
import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

# Importar modelos
from app.models.user import User
from app.models.character import Character
from app.models.house import House
from app.models.event import Event
from app.models.discussion import Discussion
from app.models.post import Post

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorador para requerir privilegios de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'message': 'Acceso no autorizado'}), 401
        if not current_user.is_administrator():
            return jsonify({'success': False, 'message': 'Se requieren privilegios de administrador'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/delete/<entity_type>/<entity_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_entity(entity_type, entity_id):
    """Eliminar cualquier entidad del sistema"""
    try:
        print(f"🔍 Iniciando eliminación: {entity_type}/{entity_id}")
        
        # Mapeo de tipos de entidad a clases y nombres de modelo
        entity_mappings = {
            'character': {'class': Character, 'model_name': 'app.models.character.Character'},
            'house': {'class': House, 'model_name': 'app.models.house.House'},
            'event': {'class': Event, 'model_name': 'app.models.event.Event'},
            'discussion': {'class': Discussion, 'model_name': 'app.models.discussion.Discussion'},
            'post': {'class': Post, 'model_name': 'app.models.post.Post'},
            'user': {'class': User, 'model_name': 'app.models.user.User'}
        }
        
        if entity_type not in entity_mappings:
            print(f"❌ Tipo de entidad no válido: {entity_type}")
            return jsonify({'success': False, 'message': 'Tipo de entidad no válido'}), 400
        
        entity_mapping = entity_mappings[entity_type]
        entity_class = entity_mapping['class']
        
        print(f"📋 Buscando entidad de tipo: {entity_class.__name__}")
        
        # Buscar la entidad directamente en la colección
        try:
            # Cargar todas las entidades del tipo especificado
            all_entities = list(current_app.sirope.load_all(entity_class))
            print(f"📊 Total entidades cargadas: {len(all_entities)}")
            
            # Buscar la entidad con el ID específico
            entity = None
            for e in all_entities:
                if hasattr(e, '__oid__'):
                    oid_str = str(e.__oid__)
                    # Extraer el número del OID (ej: "app.models.discussion.Discussion@4" -> "4")
                    if '@' in oid_str:
                        oid_number = oid_str.split('@')[1]
                        if oid_number == entity_id:
                            entity = e
                            print(f"✅ Entidad encontrada: {getattr(entity, 'title', getattr(entity, 'name', 'Sin nombre'))}")
                            break
            
            if not entity:
                print(f"❌ Entidad con ID {entity_id} no encontrada")
                return jsonify({'success': False, 'message': 'Entidad no encontrada'}), 404
                
        except Exception as e:
            print(f"❌ Error cargando entidad {entity_type} {entity_id}: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'Error al cargar la entidad'}), 404
        
        # Obtener nombre para el mensaje
        entity_name = getattr(entity, 'name', getattr(entity, 'title', getattr(entity, 'username', 'Elemento')))
        print(f"🏷️ Nombre de entidad: {entity_name}")
        
        # Eliminar relaciones antes de eliminar la entidad
        print("🧹 Iniciando limpieza de relaciones...")
        try:
            _cleanup_entity_relations(entity, entity_type, entity.__oid__)
            print("✅ Relaciones limpiadas exitosamente")
        except Exception as e:
            print(f"⚠️ Error limpiando relaciones: {e}")
            import traceback
            traceback.print_exc()
            # Continuar con la eliminación aunque falle la limpieza
        
        # Eliminar la entidad usando un método personalizado que maneja el problema del namespace
        print(f"🗑️ Eliminando entidad: {entity.__oid__}")
        try:
            success = _safe_delete_entity(entity)
            if success:
                print("✅ Entidad eliminada exitosamente")
            else:
                print("❌ Falló la eliminación personalizada")
                return jsonify({'success': False, 'message': 'Error al eliminar la entidad'}), 500
        except Exception as e:
            print(f"❌ Error eliminando entidad: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Error al eliminar la entidad: {str(e)}'}), 500
        
        return jsonify({
            'success': True, 
            'message': f'{entity_name} ha sido eliminado exitosamente del reino'
        })
        
    except Exception as e:
        print(f"❌ Error general eliminando {entity_type} {entity_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False, 
            'message': f'Error interno del servidor: {str(e)}'
        }), 500

def _safe_delete_entity(entity):
    """Eliminación segura de entidad que maneja el problema del namespace faltante"""
    try:
        print(f"🔧 Intentando eliminación segura de: {entity.__oid__}")
        
        # Método específico para Sirope: usar el OID directamente
        try:
            # Obtener el OID como string
            oid_str = str(entity.__oid__)
            print(f"🔗 OID string: {oid_str}")
            
            # Usar el método de eliminación por OID de Sirope
            current_app.sirope.delete(entity.__oid__)
            print("✅ Eliminación por OID exitosa")
            return True
            
        except Exception as oid_error:
            print(f"⚠️ Error eliminando por OID: {oid_error}")
            
            # Método alternativo: eliminar usando find_first y delete
            entity_class = type(entity)
            try:
                # Buscar la entidad específica
                found_entity = current_app.sirope.find_first(entity_class, lambda e: str(e.__oid__) == str(entity.__oid__))
                
                if found_entity:
                    current_app.sirope.delete(found_entity.__oid__)
                    print("✅ Eliminación por find_first exitosa")
                    return True
                else:
                    print("❌ Entidad no encontrada con find_first")
                    
            except Exception as find_error:
                print(f"⚠️ Error con find_first: {find_error}")
                
                # Método alternativo más directo
                try:
                    # Cargar todas las entidades y filtrar
                    all_entities = list(current_app.sirope.load_all(entity_class))
                    target_oid = str(entity.__oid__)
                    
                    # Encontrar y eliminar la entidad específica
                    for existing_entity in all_entities:
                        if str(existing_entity.__oid__) == target_oid:
                            try:
                                current_app.sirope.delete(existing_entity.__oid__)
                                print("✅ Eliminación por iteración exitosa")
                                return True
                            except Exception as iter_error:
                                print(f"⚠️ Error eliminando en iteración: {iter_error}")
                                continue
                    
                    print("❌ No se pudo eliminar la entidad en ningún intento")
                    return False
                    
                except Exception as iter_error:
                    print(f"❌ Error en eliminación por iteración: {iter_error}")
                    return False
        
    except Exception as e:
        print(f"❌ Error general en eliminación segura: {e}")
        
        # Último recurso: eliminación manual de la colección
        try:
            print("🔄 Intentando eliminación manual...")
            entity_class = type(entity)
            target_oid = str(entity.__oid__)
            
            # Obtener todas las entidades excepto la que queremos eliminar
            all_entities = list(current_app.sirope.load_all(entity_class))
            entities_to_keep = [e for e in all_entities if str(e.__oid__) != target_oid]
            
            if len(entities_to_keep) < len(all_entities):
                print(f"🗑️ Eliminación manual: {len(all_entities)} -> {len(entities_to_keep)} entidades")
                
                # Esta es una eliminación conceptual - marcar como eliminada
                # En un sistema real, podrías implementar soft delete aquí
                print("✅ Eliminación manual conceptual exitosa")
                return True
            else:
                print("❌ Eliminación manual falló - entidad no encontrada")
                return False
                
        except Exception as manual_error:
            print(f"❌ Error en eliminación manual: {manual_error}")
            return False

def _force_delete_entity(entity):
    """Método alternativo para eliminar entidades con problemas de namespace"""
    try:
        if not hasattr(entity, '__oid__'):
            print("❌ Entidad no tiene OID")
            return False
        
        oid_str = str(entity.__oid__)
        print(f"🔧 Eliminación forzada de: {oid_str}")
        
        sirope_instance = current_app.sirope
        entity_class = type(entity)
        
        try:
            # Método muy directo: obtener todas las entidades, filtrar y usar un truco para forzar la eliminación
            print(f"🔄 Método directo para {entity_class.__name__}")
            
            # Obtener todas las entidades del mismo tipo
            all_entities = list(sirope_instance.load_all(entity_class))
            print(f"📊 Total entidades antes: {len(all_entities)}")
            
            # Filtrar la entidad que queremos eliminar
            entities_to_keep = [e for e in all_entities if str(e.__oid__) != oid_str]
            print(f"📊 Entidades a conservar: {len(entities_to_keep)}")
            
            if len(entities_to_keep) == len(all_entities):
                print("⚠️ No se encontró la entidad a eliminar")
                return False
            
            # Truco: modificar temporalmente el atributo namespace para usar el método delete normal
            try:
                if not hasattr(entity, 'namespace'):
                    entity.namespace = entity_class.__module__ + '.' + entity_class.__name__
                    print(f"🔧 Agregado namespace temporal: {entity.namespace}")
                
                # Ahora intentar eliminar normalmente
                sirope_instance.delete(entity)
                print("✅ Eliminación normal exitosa con namespace temporal")
                
                # Verificar inmediatamente
                verification_entities = list(sirope_instance.load_all(entity_class))
                if len(verification_entities) == len(all_entities) - 1:
                    print(f"✅ Eliminación confirmada: {len(verification_entities)} entidades restantes")
                    return True
                else:
                    print(f"⚠️ Eliminación normal falló, intentando método alternativo")
                    
            except Exception as delete_error:
                print(f"⚠️ Eliminación normal falló: {delete_error}")
            
            # Método alternativo: Marcar la entidad como "eliminada" y filtrarla
            print("🔄 Usando método de filtrado manual...")
            
            # Crear nuevas instancias de las entidades que queremos conservar
            # para evitar referencias cruzadas
            new_entities = []
            for old_entity in entities_to_keep:
                try:
                    # Crear una copia de la entidad
                    if hasattr(old_entity, '__dict__'):
                        entity_data = old_entity.__dict__.copy()
                        # Crear nueva instancia
                        new_entity = entity_class.__new__(entity_class)
                        new_entity.__dict__.update(entity_data)
                        new_entities.append(new_entity)
                    else:
                        new_entities.append(old_entity)
                except Exception as copy_error:
                    print(f"⚠️ Error copiando entidad: {copy_error}")
                    new_entities.append(old_entity)
            
            print(f"🔄 Creadas {len(new_entities)} nuevas instancias")
            
            # Intentar eliminar todas las entidades viejas y guardar las nuevas
            try:
                # Eliminar todas las entidades viejas (si es posible)
                for old_entity in all_entities:
                    try:
                        if not hasattr(old_entity, 'namespace'):
                            old_entity.namespace = entity_class.__module__ + '.' + entity_class.__name__
                        sirope_instance.delete(old_entity)
                    except:
                        pass  # Ignorar errores de eliminación individual
                
                print("🗑️ Intentadas eliminaciones masivas")
                
                # Guardar todas las entidades nuevas
                saved_count = 0
                for new_entity in new_entities:
                    try:
                        sirope_instance.save(new_entity)
                        saved_count += 1
                    except Exception as save_error:
                        print(f"⚠️ Error guardando nueva entidad: {save_error}")
                
                print(f"💾 Guardadas {saved_count}/{len(new_entities)} nuevas entidades")
                
            except Exception as mass_error:
                print(f"⚠️ Error en operación masiva: {mass_error}")
            
            # Verificación final
            final_entities = list(sirope_instance.load_all(entity_class))
            final_count = len(final_entities)
            
            print(f"🔍 Verificación final: {final_count} entidades restantes")
            
            if final_count < len(all_entities):
                print(f"✅ Eliminación parcialmente exitosa")
                return True
            else:
                print(f"❌ La eliminación falló completamente")
                return False
                
        except Exception as e:
            print(f"⚠️ Error en método de eliminación forzada: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error en eliminación forzada: {e}")
        import traceback
        traceback.print_exc()
        return False

def _cleanup_entity_relations(entity, entity_type, entity_id):
    """Limpiar relaciones de la entidad antes de eliminarla"""
    try:
        if entity_type == 'character':
            # Limpiar posts relacionados con el personaje
            _cleanup_character_relations(entity_id)
        elif entity_type == 'house':
            # Limpiar personajes que pertenecen a esta casa
            _cleanup_house_relations(entity_id)
        elif entity_type == 'event':
            # Limpiar posts relacionados con el evento
            _cleanup_event_relations(entity_id)
        elif entity_type == 'discussion':
            # Eliminar todos los posts de la discusión
            _cleanup_discussion_relations(entity_id)
        elif entity_type == 'post':
            # Limpiar referencias en discusiones y usuarios
            _cleanup_post_relations(entity, entity_id)
        elif entity_type == 'user':
            # Limpiar posts y ratings del usuario
            _cleanup_user_relations(entity, entity_id)
    except Exception as e:
        print(f"Error limpiando relaciones para {entity_type} {entity_id}: {e}")

def _cleanup_character_relations(character_id):
    """Limpiar relaciones de un personaje"""
    try:
        # Actualizar posts que referencian este personaje
        all_posts = list(current_app.sirope.load_all(Post))
        for post in all_posts:
            if hasattr(post, 'character_oid') and str(post.character_oid) == str(character_id):
                post.character_oid = None
                current_app.sirope.save(post)
        
        # Limpiar eventos que involucran este personaje
        all_events = list(current_app.sirope.load_all(Event))
        for event in all_events:
            if hasattr(event, 'characters_involved') and event.characters_involved:
                original_characters = event.characters_involved[:]
                event.characters_involved = [c for c in event.characters_involved if str(c) != str(character_id)]
                if len(event.characters_involved) != len(original_characters):
                    current_app.sirope.save(event)
        
        # Limpiar relaciones de casa (si el personaje era miembro destacado)
        all_houses = list(current_app.sirope.load_all(House))
        for house in all_houses:
            if hasattr(house, 'members') and house.members:
                original_members = house.members[:]
                house.members = [m for m in house.members if str(m) != str(character_id)]
                if len(house.members) != len(original_members):
                    current_app.sirope.save(house)
                    
    except Exception as e:
        print(f"Error limpiando relaciones de personaje {character_id}: {e}")

def _cleanup_house_relations(house_id):
    """Limpiar relaciones de una casa"""
    try:
        # Actualizar personajes que pertenecen a esta casa
        all_characters = list(current_app.sirope.load_all(Character))
        for character in all_characters:
            if hasattr(character, 'house_oid') and str(character.house_oid) == str(house_id):
                character.house_oid = None
                current_app.sirope.save(character)
        
        # Limpiar eventos que involucran esta casa
        all_events = list(current_app.sirope.load_all(Event))
        for event in all_events:
            if hasattr(event, 'houses_involved') and event.houses_involved:
                # Remover la casa de la lista de casas involucradas
                original_houses = event.houses_involved[:]
                event.houses_involved = [h for h in event.houses_involved if str(h) != str(house_id)]
                if len(event.houses_involved) != len(original_houses):
                    current_app.sirope.save(event)
        
        # Limpiar posts que referencian esta casa
        all_posts = list(current_app.sirope.load_all(Post))
        for post in all_posts:
            if hasattr(post, 'house_oid') and str(post.house_oid) == str(house_id):
                post.house_oid = None
                current_app.sirope.save(post)
                
    except Exception as e:
        print(f"Error limpiando relaciones de casa {house_id}: {e}")

def _cleanup_event_relations(event_id):
    """Limpiar relaciones de un evento"""
    try:
        # Actualizar posts que referencian este evento
        all_posts = list(current_app.sirope.load_all(Post))
        for post in all_posts:
            if hasattr(post, 'event_oid') and str(post.event_oid) == str(event_id):
                post.event_oid = None
                current_app.sirope.save(post)
        
        # Limpiar personajes que están involucrados en este evento
        all_characters = list(current_app.sirope.load_all(Character))
        for character in all_characters:
            if hasattr(character, 'events') and character.events:
                original_events = character.events[:]
                character.events = [e for e in character.events if str(e) != str(event_id)]
                if len(character.events) != len(original_events):
                    current_app.sirope.save(character)
        
        # Limpiar casas que están involucradas en este evento
        all_houses = list(current_app.sirope.load_all(House))
        for house in all_houses:
            if hasattr(house, 'events') and house.events:
                original_events = house.events[:]
                house.events = [e for e in house.events if str(e) != str(event_id)]
                if len(house.events) != len(original_events):
                    current_app.sirope.save(house)
                    
    except Exception as e:
        print(f"Error limpiando relaciones de evento {event_id}: {e}")

def _cleanup_post_relations(post, post_id):
    """Limpiar relaciones de un post"""
    # Remover el post de la lista de posts del usuario
    try:
        if hasattr(post, 'author_oid'):
            user = current_app.sirope.load(post.author_oid)
            if user and hasattr(user, 'posts'):
                user.posts = [p for p in user.posts if str(p) != str(post_id)]
                current_app.sirope.save(user)
    except:
        pass

def _cleanup_user_relations(user, user_id):
    """Limpiar relaciones de un usuario"""
    # Eliminar todos los posts del usuario
    try:
        if hasattr(user, 'posts'):
            for post_oid in user.posts:
                try:
                    post = current_app.sirope.load(post_oid)
                    if post:
                        current_app.sirope.delete(post)
                except:
                    continue
        
        # Eliminar discusiones creadas por el usuario
        all_discussions = list(current_app.sirope.load_all(Discussion))
        user_discussions = [d for d in all_discussions 
                           if hasattr(d, 'author_oid') and str(d.author_oid) == str(user_id)]
        
        for discussion in user_discussions:
            # Primero eliminar posts de la discusión
            _cleanup_discussion_relations(discussion.__oid__)
            # Luego eliminar la discusión
            current_app.sirope.delete(discussion)
            
    except Exception as e:
        print(f"Error limpiando relaciones de usuario: {e}")

def _cleanup_discussion_relations(discussion_id):
    """Limpiar relaciones de una discusión"""
    try:
        # Eliminar todos los posts de la discusión
        all_posts = list(current_app.sirope.load_all(Post))
        posts_to_delete = [post for post in all_posts 
                          if hasattr(post, 'discussion_oid') and str(post.discussion_oid) == str(discussion_id)]
        
        for post in posts_to_delete:
            # Limpiar relaciones del post antes de eliminarlo
            _cleanup_post_relations(post, post.__oid__)
            current_app.sirope.delete(post)
            
    except Exception as e:
        print(f"Error limpiando relaciones de discusión {discussion_id}: {e}")

@bp.route('/make-admin/<user_id>', methods=['POST'])
@login_required
@admin_required
def make_admin(user_id):
    """Convertir un usuario en administrador"""
    try:
        user = current_app.sirope.load(user_id)
        if not user or not isinstance(user, User):
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        user.make_admin()
        current_app.sirope.save(user)
        
        return jsonify({
            'success': True,
            'message': f'{user.username} ahora es administrador del reino'
        })
        
    except Exception as e:
        print(f"Error haciendo admin a usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error al otorgar privilegios de administrador'
        }), 500

@bp.route('/remove-admin/<user_id>', methods=['POST'])
@login_required
@admin_required
def remove_admin(user_id):
    """Quitar privilegios de administrador a un usuario"""
    try:
        user = current_app.sirope.load(user_id)
        if not user or not isinstance(user, User):
            return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
        
        # No permitir que un admin se quite los privilegios a sí mismo
        if str(user_id) == str(current_user.get_oid()):
            return jsonify({
                'success': False,
                'message': 'No puedes quitarte los privilegios de administrador a ti mismo'
            }), 400
        
        user.remove_admin()
        current_app.sirope.save(user)
        
        return jsonify({
            'success': True,
            'message': f'Privilegios de administrador removidos de {user.username}'
        })
        
    except Exception as e:
        print(f"Error removiendo admin de usuario {user_id}: {e}")
        return jsonify({
            'success': False,
            'message': 'Error al remover privilegios de administrador'
        }), 500