from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin):
    def __init__(self, username, email, password_hash=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.now()
        self.posts = []  # Lista de OIDs de posts del usuario
        self.ratings = {}  # Diccionario {entity_oid: rating} para evitar ratings duplicados
        self.favorites = []  # Lista de OIDs de entidades favoritas
        self.avatar_url = None  # URL del avatar del usuario
        self.is_admin = False  # Campo para identificar administradores
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Requerido por Flask-Login"""
        return str(self.__oid__) if hasattr(self, '__oid__') else None
    
    def get_oid(self):
        """Obtener el OID del usuario"""
        return self.__oid__ if hasattr(self, '__oid__') else None
    
    def add_post(self, post_oid):
        """Agregar un post al historial del usuario"""
        if post_oid not in self.posts:
            self.posts.append(post_oid)
    
    def add_rating(self, entity_oid, rating):
        """Agregar/actualizar rating para una entidad"""
        self.ratings[str(entity_oid)] = rating
    
    def update_rating(self, entity_oid, new_rating):
        """Actualizar rating existente para una entidad"""
        self.ratings[str(entity_oid)] = new_rating
    
    def get_rating_for(self, entity_oid):
        """Obtener rating del usuario para una entidad específica"""
        return self.ratings.get(str(entity_oid))
    
    def toggle_favorite(self, entity_oid):
        """Agregar o quitar una entidad de favoritos"""
        entity_str = str(entity_oid)
        if hasattr(self, 'favorites') and self.favorites is not None:
            if entity_str in self.favorites:
                self.favorites.remove(entity_str)
                return False
            else:
                self.favorites.append(entity_str)
                return True
        else:
            # Inicializar favoritos si no existe
            self.favorites = [entity_str]
            return True
    
    def is_favorite(self, entity_oid):
        """Verificar si una entidad está en favoritos"""
        if not hasattr(self, 'favorites') or self.favorites is None:
            return False
        return str(entity_oid) in self.favorites
    
    def get_total_posts(self):
        """Obtener el total de posts del usuario"""
        return len(self.posts)
    
    def get_total_ratings(self):
        """Obtener el total de ratings realizados por el usuario"""
        return len(self.ratings)
    
    def get_total_likes(self):
        """Obtener el total de likes recibidos en todos los posts del usuario"""
        # Este método requiere acceso a la base de datos para contar likes
        # Por ahora retornamos 0, se puede implementar más tarde
        return 0
    
    def make_admin(self):
        """Convertir usuario en administrador"""
        self.is_admin = True
    
    def remove_admin(self):
        """Quitar privilegios de administrador"""
        self.is_admin = False
    
    def is_administrator(self):
        """Verificar si el usuario es administrador"""
        return getattr(self, 'is_admin', False)
    
    def __str__(self):
        return f"User({self.username})"