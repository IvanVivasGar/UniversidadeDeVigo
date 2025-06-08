from datetime import datetime

class Post:
    def __init__(self, title, content, author_oid):
        self.title = title
        self.content = content
        self.author_oid = author_oid  # OID del usuario que creó el post
        self.created_at = datetime.now()
        self.likes = []  # Lista de OIDs de usuarios que dieron like
        self.comments = []  # Lista de comentarios
        self.like_count = 0
    
    def add_like(self, user_oid):
        """Agregar like de un usuario"""
        if user_oid not in self.likes:
            self.likes.append(user_oid)
            self.like_count = len(self.likes)
            return True
        return False
    
    def remove_like(self, user_oid):
        """Quitar like de un usuario"""
        if user_oid in self.likes:
            self.likes.remove(user_oid)
            self.like_count = len(self.likes)
            return True
        return False
    
    def add_comment(self, comment):
        """Agregar un comentario al post"""
        self.comments.append(comment)
    
    def get_comments_count(self):
        """Obtener número de comentarios"""
        return len(self.comments)
    
    def has_liked(self, user_oid):
        """Verificar si un usuario ya dio like"""
        return user_oid in self.likes
    
    def get_time_ago(self):
        """Obtener tiempo transcurrido desde la creación"""
        now = datetime.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "hace unos segundos"
    
    def __str__(self):
        return f"Post({self.title})"


class Comment:
    def __init__(self, content, author_oid, post_oid):
        self.content = content
        self.author_oid = author_oid  # OID del usuario que comentó
        self.post_oid = post_oid  # OID del post al que pertenece
        self.created_at = datetime.now()
        self.likes = []  # Lista de OIDs de usuarios que dieron like
        self.like_count = 0
    
    def add_like(self, user_oid):
        """Agregar like de un usuario"""
        if user_oid not in self.likes:
            self.likes.append(user_oid)
            self.like_count = len(self.likes)
            return True
        return False
    
    def remove_like(self, user_oid):
        """Quitar like de un usuario"""
        if user_oid in self.likes:
            self.likes.remove(user_oid)
            self.like_count = len(self.likes)
            return True
        return False
    
    def has_liked(self, user_oid):
        """Verificar si un usuario ya dio like"""
        return user_oid in self.likes
    
    def get_time_ago(self):
        """Obtener tiempo transcurrido desde la creación"""
        now = datetime.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "hace unos segundos"
    
    def __str__(self):
        return f"Comment(post_oid={self.post_oid})"