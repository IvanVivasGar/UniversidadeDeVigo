import os
from werkzeug.utils import secure_filename
from flask import current_app
import uuid

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder='general'):
    """Guardar archivo subido y retornar la URL"""
    if file and allowed_file(file.filename):
        # Crear nombre único para evitar conflictos
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Crear directorio si no existe
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_path, exist_ok=True)
        
        # Guardar archivo
        file_path = os.path.join(upload_path, unique_filename)
        file.save(file_path)
        
        # Retornar URL relativa
        return f"/static/images/uploads/{folder}/{unique_filename}"
    
    return None

def get_entity_by_name(sirope_instance, entity_class, name):
    """Buscar entidad por nombre"""
    try:
        # Para usuarios, buscar por username
        if entity_class.__name__ == 'User':
            return sirope_instance.find_first(entity_class, lambda e: e.username.lower() == name.lower())
        # Para otras entidades, buscar por name
        else:
            return sirope_instance.find_first(entity_class, lambda e: e.name.lower() == name.lower())
    except:
        return None

def search_entities(sirope_instance, entity_class, search_term):
    """Buscar entidades que contengan el término de búsqueda"""
    try:
        if not search_term:
            return list(sirope_instance.load_all(entity_class))
        
        search_term = search_term.lower()
        return list(sirope_instance.filter(
            entity_class, 
            lambda e: search_term in e.name.lower() or search_term in e.description.lower()
        ))
    except:
        return []

def get_latest_entities(sirope_instance, entity_class, limit=2):
    """Obtener las últimas entidades creadas"""
    try:
        entities = list(sirope_instance.load_all(entity_class))
        entities.sort(key=lambda e: e.created_at, reverse=True)
        return entities[:limit]
    except:
        return []

def calculate_average_rating(ratings_list):
    """Calcular rating promedio de una lista de ratings"""
    if not ratings_list:
        return 0
    return round(sum(ratings_list) / len(ratings_list), 1)