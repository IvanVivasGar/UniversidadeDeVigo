from datetime import datetime

class Character:
    def __init__(self, name, status, house_affiliation, description, image_url=None):
        self.name = name
        self.status = status  # "Alive", "Dead", "Unknown"
        self.house_affiliation = house_affiliation  # OID de la casa
        self.description = description
        self.image_url = image_url
        self.created_at = datetime.now()
        self.ratings = []  # Lista de ratings de usuarios
        self.total_rating = 0.0  # Rating promedio
        self.rating_count = 0
    
    @property
    def house(self):
        """Propiedad para obtener el nombre de la casa si está afiliado"""
        if self.house_affiliation:
            try:
                # Esta propiedad debe ser usada en el contexto donde sirope esté disponible
                # En las vistas, mejor pasar la casa como variable separada
                return "Casa afiliada"
            except:
                return None
        return None
    
    def add_rating(self, rating):
        """Agregar un nuevo rating (1-5 estrellas)"""
        if 1 <= rating <= 5:
            self.ratings.append(rating)
            self.rating_count = len(self.ratings)
            self.total_rating = sum(self.ratings) / self.rating_count
    
    def update_rating(self, old_rating, new_rating):
        """Actualizar un rating existente"""
        if 1 <= old_rating <= 5 and 1 <= new_rating <= 5:
            if old_rating in self.ratings:
                # Remover la valoración anterior
                self.ratings.remove(old_rating)
                # Agregar la nueva valoración
                self.ratings.append(new_rating)
                # Recalcular promedio
                self.rating_count = len(self.ratings)
                self.total_rating = sum(self.ratings) / self.rating_count if self.rating_count > 0 else 0
    
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
    
    def __str__(self):
        return f"Character({self.name})"