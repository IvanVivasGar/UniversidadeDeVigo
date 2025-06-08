from datetime import datetime

class Event:
    def __init__(self, name, season, episode, description, image_urls=None):
        self.name = name
        self.season = season
        self.episode = episode
        self.description = description
        self.image_urls = image_urls or []  # Lista de URLs de imágenes
        self.created_at = datetime.now()
        self.characters_involved = []  # Lista de OIDs de personajes
        self.houses_involved = []  # Lista de OIDs de casas
        self.importance_rating = 1  # Rating de importancia 1-5
        self.user_ratings = {}  # Diccionario {user_oid: rating} para ratings individuales
        self.total_rating = 0.0  # Rating promedio
        self.rating_count = 0
    
    def add_image(self, image_url):
        """Agregar una nueva imagen"""
        if image_url not in self.image_urls:
            self.image_urls.append(image_url)
    
    def add_character(self, character_oid):
        """Agregar un personaje involucrado"""
        if character_oid not in self.characters_involved:
            self.characters_involved.append(character_oid)
    
    def add_house(self, house_oid):
        """Agregar una casa involucrada"""
        if house_oid not in self.houses_involved:
            self.houses_involved.append(house_oid)
    
    def set_importance_rating(self, rating):
        """Establecer rating de importancia (1-5)"""
        if 1 <= rating <= 5:
            self.importance_rating = rating
    
    def add_user_rating(self, user_oid, rating):
        """Agregar o actualizar rating de un usuario específico"""
        if 1 <= rating <= 5:
            # Convertir OID a string para usar como clave
            user_key = str(user_oid)
            self.user_ratings[user_key] = rating
            self._recalculate_average()
            return True
        return False
    
    def get_user_rating(self, user_oid):
        """Obtener el rating de un usuario específico"""
        user_key = str(user_oid)
        return self.user_ratings.get(user_key, 0)
    
    def remove_user_rating(self, user_oid):
        """Remover el rating de un usuario"""
        user_key = str(user_oid)
        if user_key in self.user_ratings:
            del self.user_ratings[user_key]
            self._recalculate_average()
            return True
        return False
    
    def _recalculate_average(self):
        """Recalcular el promedio y contador de ratings"""
        if self.user_ratings:
            ratings_list = list(self.user_ratings.values())
            self.total_rating = sum(ratings_list) / len(ratings_list)
            self.rating_count = len(ratings_list)
        else:
            self.total_rating = 0.0
            self.rating_count = 0
    
    def get_average_rating(self):
        """Obtener rating promedio"""
        return round(self.total_rating, 1) if self.total_rating > 0 else 0.0
    
    def get_rating_count(self):
        """Obtener número total de ratings"""
        return self.rating_count
    
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
        return self.image_urls[0] if self.image_urls else None
    
    def get_season_episode_display(self):
        """Obtener formato de temporada y episodio"""
        return f"S{self.season:02d}E{self.episode:02d}"
    
    def __str__(self):
        return f"Event({self.name} - {self.get_season_episode_display()})"