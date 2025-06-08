from datetime import datetime

class House:
    def __init__(self, name, motto, description, images=None):
        self.name = name
        self.motto = motto
        self.description = description
        self.images = images or []  # Lista de URLs de imágenes (cambiado de image_urls)
        self.region = None  # Región de Westeros
        self.status = None  # Estado: mayor, menor, extinta
        self.created_at = datetime.now()
        self.members = []  # Lista de OIDs de personajes
        self.events = []  # Lista de OIDs de eventos
        self.ratings = []  # Lista de ratings de usuarios
        self.total_rating = 0.0  # Rating promedio
        self.rating_count = 0
    
    def add_image(self, image_url):
        """Agregar una nueva imagen"""
        if image_url not in self.images:
            self.images.append(image_url)
    
    def add_member(self, character_oid):
        """Agregar un miembro a la casa"""
        if character_oid not in self.members:
            self.members.append(character_oid)
    
    def add_event(self, event_oid):
        """Agregar un evento relacionado"""
        if event_oid not in self.events:
            self.events.append(event_oid)
    
    def add_rating(self, rating):
        """Agregar un nuevo rating (1-5 estrellas)"""
        if 1 <= rating <= 5:
            self.ratings.append(rating)
            self.rating_count = len(self.ratings)
            self.total_rating = sum(self.ratings) / self.rating_count
    
    def get_average_rating(self):
        """Obtener rating promedio"""
        return round(self.total_rating, 1) if self.total_rating > 0 else 0
    
    def get_star_display(self):
        """Obtener representación visual de estrellas"""
        rating = self.get_average_rating()
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return {
            'full': full_stars,
            'half': half_star,
            'empty': empty_stars
        }
    
    def get_main_image(self):
        """Obtener la imagen principal (primera de la lista)"""
        return self.images[0] if self.images else None
    
    @property
    def sigil_url(self):
        """Alias para compatibilidad - obtiene la primera imagen como sigil"""
        return self.get_main_image()
    
    def __str__(self):
        return f"House({self.name})"