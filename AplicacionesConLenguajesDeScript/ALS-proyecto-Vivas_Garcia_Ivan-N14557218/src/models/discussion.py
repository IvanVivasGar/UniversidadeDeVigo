from datetime import datetime

class Discussion:
    def __init__(self, title, content, author_oid, category="general"):
        self.title = title
        self.content = content
        self.author_oid = author_oid  # OID del usuario que creó la discusión
        self.category = category
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.likes = []  # Lista de OIDs de usuarios que dieron like
        self.replies = []  # Lista de OIDs de respuestas
        self.like_count = 0
        self.reply_count = 0
        self.view_count = 0
        self.is_pinned = False
        self.is_closed = False
        self.tags = []  # Lista de tags/etiquetas
        self.image_url = None  # URL de imagen opcional
        self.last_activity = datetime.now()  # Para ordenar por actividad reciente
    
    def get_author_name(self, sirope):
        """Obtener el nombre del autor de la discusión"""
        try:
            from app.models.user import User
            author = sirope.find_first(User, lambda u: u.__oid__ == self.author_oid)
            return author.username if author else "Usuario desconocido"
        except:
            return "Usuario desconocido"
    
    def get_oid(self):
        """Obtener el OID de la discusión"""
        return str(self.__oid__) if hasattr(self, '__oid__') else None
        
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
    
    def add_reply(self, reply_oid):
        """Agregar una respuesta a la discusión"""
        self.replies.append(reply_oid)
        self.reply_count = len(self.replies)
        self.last_activity = datetime.now()
    
    def get_replies_count(self):
        """Obtener número de respuestas"""
        return len(self.replies)
    
    def add_tag(self, tag):
        """Agregar un tag a la discusión"""
        if tag and tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag):
        """Remover un tag de la discusión"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def increment_views(self):
        """Incrementar contador de visualizaciones"""
        self.view_count += 1
    
    def pin(self):
        """Fijar la discusión"""
        self.is_pinned = True
    
    def unpin(self):
        """Desfijar la discusión"""
        self.is_pinned = False
    
    def close(self):
        """Cerrar la discusión"""
        self.is_closed = True
    
    def reopen(self):
        """Reabrir la discusión"""
        self.is_closed = False
    
    def update_content(self, new_content):
        """Actualizar el contenido de la discusión"""
        self.content = new_content
        self.updated_at = datetime.now()
    
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
        return f"Discussion(title='{self.title}', author={self.author_oid})"


class DiscussionReply:
    def __init__(self, content, author_oid, discussion_oid, parent_reply_oid=None):
        self.content = content
        self.author_oid = author_oid
        self.discussion_oid = discussion_oid
        self.parent_reply_oid = parent_reply_oid  # Para respuestas anidadas
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.likes = []
        self.like_count = 0
        self.is_solution = False  # Marcar como solución si aplica
    
    def get_author_name(self, sirope):
        """Obtener el nombre del autor de la respuesta"""
        try:
            from app.models.user import User
            author = sirope.find_first(User, lambda u: u.__oid__ == self.author_oid)
            return author.username if author else "Usuario desconocido"
        except:
            return "Usuario desconocido"
    
    def get_oid(self):
        """Obtener el OID de la respuesta"""
        return str(self.__oid__) if hasattr(self, '__oid__') else None
        
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
    
    def mark_as_solution(self):
        """Marcar esta respuesta como solución"""
        self.is_solution = True
    
    def unmark_as_solution(self):
        """Desmarcar esta respuesta como solución"""
        self.is_solution = False
    
    def update_content(self, new_content):
        """Actualizar el contenido de la respuesta"""
        self.content = new_content
        self.updated_at = datetime.now()
    
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
        return f"DiscussionReply(content='{self.content[:50]}...', author={self.author_oid})"