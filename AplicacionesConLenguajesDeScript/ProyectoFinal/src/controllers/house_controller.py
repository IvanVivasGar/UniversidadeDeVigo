import sirope
from models.house import House
from sirope.oid import OID

class HouseController:
    def __init__(self, srp: sirope.Sirope):
        self.srp = srp

    def create_house(self, name, sigil, words, region, description, image_url=None):
        """Crea una nueva casa"""
        house = House(name, sigil, words, region, description, image_url)
        # Guardar y obtener el OID asignado por Sirope
        house._oid = self.srp.save(house)
        return house

    def get_all_houses(self):
        """Obtiene todas las casas"""
        houses = []
        try:
            # Usar load_all en lugar de filter
            for house in self.srp.load_all(House):
                if house:
                    houses.append(house)
        except Exception as e:
            print(f"Error al cargar casas: {e}")
        return houses

    def get_house_by_id(self, house_id):
        """Obtiene una casa por su ID"""
        if not house_id:
            return None
            
        try:
            if isinstance(house_id, str):
                # Verificar si ya tiene el formato correcto para OID
                if '@' in house_id:
                    # Extraer solo el número después del @ si es una representación como "models.house.House@3"
                    parts = house_id.split('@')
                    if len(parts) > 1:
                        house_id = parts[1]
                house_id = OID(house_id)
            return self.srp.load(house_id)
        except Exception as e:
            print(f"Error al cargar casa: {e}")
            return None

    def update_house(self, house_id, name, sigil, words, region, description, image_url=None):
        """Actualiza una casa existente"""
        house = self.srp.load(house_id)
        if house:
            house._name = name
            house._sigil = sigil
            house._words = words
            house._region = region
            house._description = description
            if image_url:
                house._image_url = image_url
            self.srp.save(house)
            return True, "Casa actualizada correctamente"
        return False, "Casa no encontrada"

    def delete_house(self, house_id):
        """Elimina una casa"""
        # En una aplicación real, deberíamos asegurarnos de actualizar todos los personajes
        # que pertenecen a esta casa para mantener la integridad del sistema
        house = self.srp.load(house_id)
        if house:
            self.srp.delete(house)
            return True, "Casa eliminada correctamente"
        return False, "Casa no encontrada"
        
    def add_member_to_house(self, house_id, character_oid):
        """Agrega un personaje a una casa"""
        try:
            if isinstance(house_id, str):
                house_id = OID(house_id)
                
            house = self.srp.load(house_id)
            if not house:
                return False, "Casa no encontrada"
                
            # Asegurarse de que character_oid sea un OID
            if isinstance(character_oid, str):
                character_oid = OID(character_oid)
                
            if house.add_member(character_oid):
                self.srp.save(house)
                return True, "Personaje agregado a la casa correctamente"
            return False, "El personaje ya pertenece a esta casa"
        except Exception as e:
            return False, f"Error al agregar el personaje a la casa: {str(e)}"
    
    def remove_member_from_house(self, house_id, character_oid):
        """Elimina un personaje de una casa"""
        try:
            if isinstance(house_id, str):
                house_id = OID(house_id)
                
            house = self.srp.load(house_id)
            if not house:
                return False, "Casa no encontrada"
                
            # Asegurarse de que character_oid sea un OID
            if isinstance(character_oid, str):
                character_oid = OID(character_oid)
                
            if house.remove_member(character_oid):
                self.srp.save(house)
                return True, "Personaje eliminado de la casa correctamente"
            return False, "El personaje no pertenece a esta casa"
        except Exception as e:
            return False, f"Error al eliminar el personaje de la casa: {str(e)}"
    
    def search_houses(self, query):
        """
        Busca casas que coincidan con el término de búsqueda
        """
        all_houses = self.get_all_houses()
        
        # Filtrar casas que coincidan con la búsqueda en nombre o descripción
        query = query.lower()
        results = [house for house in all_houses 
                  if query in house.name.lower() or 
                     (house.description and query in house.description.lower()) or
                     (house.region and query in house.region.lower())]
        
        return results
    
    def get_recent_houses(self, limit=3):
        """Obtiene las casas más recientes (basado en OID)"""
        try:
            all_houses = self.get_all_houses()
            # Filtrar casas que tengan OID válido
            houses_with_oid = [house for house in all_houses if hasattr(house, '_oid') and house._oid is not None]
            # Ordenar por OID (los más recientes tienen OID más alto)
            sorted_houses = sorted(houses_with_oid, key=lambda x: str(x._oid), reverse=True)
            return sorted_houses[:limit]
        except Exception as e:
            print(f"Error al obtener casas recientes: {e}")
            return []