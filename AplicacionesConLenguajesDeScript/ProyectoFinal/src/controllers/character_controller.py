import sirope
from models.character import Character

class CharacterController:
    def __init__(self, srp: sirope.Sirope):
        self.srp = srp

    def create_character(self, name, title, house_oid, status, description, image_url=None):
        """Crea un nuevo personaje"""
        character = Character(name, title, description, image_url, 1, status, house_oid)
        # Guardar y obtener el OID asignado por Sirope
        character._oid = self.srp.save(character)
        return character

    def get_all_characters(self):
        """Obtiene todos los personajes"""
        characters = []
        try:
            # Obtener todos los personajes de manera simple y eficiente
            for character in self.srp.load_all(Character):
                if character and hasattr(character, 'name'):
                    # Sirope automáticamente asigna el _oid cuando carga objetos
                    characters.append(character)
                    
            print(f"DEBUG: Se cargaron {len(characters)} personajes con OIDs asignados")
                
        except Exception as e:
            print(f"Error al cargar personajes: {e}")
        return characters

    def get_character_by_id(self, character_id):
        """Obtiene un personaje por su ID"""
        if not character_id:
            return None
            
        try:
            from sirope.oid import OID
            # Si es una cadena, intenta convertirla a OID
            if isinstance(character_id, str):
                # Verificar si ya tiene el formato correcto para OID
                if '@' in character_id:
                    # Extraer solo el número después del @ si es una representación como "models.character.Character@3"
                    parts = character_id.split('@')
                    if len(parts) > 1:
                        character_id = parts[1]
                character_id = OID(character_id)
            
            character = self.srp.load(character_id)
            if character:
                character._oid = character_id  # Asegurar que el OID esté asignado
            return character
        except Exception as e:
            print(f"Error al cargar personaje (ID: {character_id}): {e}")
            return None

    def get_characters_by_house(self, house_oid):
        """Obtiene todos los personajes de una casa específica"""
        characters = []
        try:
            # Usar load_all en lugar de find
            for character in self.srp.load_all(Character):
                if character and character.house_id == house_oid:
                    characters.append(character)
        except Exception as e:
            print(f"Error al cargar personajes de la casa: {e}")
        return characters

    def update_character(self, character_id, name, title, house_oid, status, description, image_url=None):
        """Actualiza un personaje existente"""
        character = self.get_character_by_id(character_id)
        if character:
            character.name = name
            character.title = title
            character.house_id = house_oid
            character.status = status
            character.description = description
            if image_url:
                character.image_url = image_url
            self.srp.save(character)
            return True, "Personaje actualizado correctamente"
        return False, "Personaje no encontrado"
        
    def delete_character(self, character_id):
        """Elimina un personaje"""
        character = self.get_character_by_id(character_id)
        if character:
            self.srp.delete(character)
            return True, "Personaje eliminado correctamente"
        return False, "Personaje no encontrado"
        
    def add_rating(self, character_id, rating):
        """Añade una valoración a un personaje"""
        character = self.get_character_by_id(character_id)
        if character:
            # Aquí podrías implementar un sistema de ratings si lo necesitas
            return True, "Valoración añadida correctamente"
        return False, "Personaje no encontrado"
        
    def search_characters(self, query):
        """
        Busca personajes que coincidan con el término de búsqueda
        """
        all_characters = self.get_all_characters()
        
        # Filtrar personajes que coincidan con la búsqueda en nombre o descripción
        query = query.lower()
        results = [character for character in all_characters 
                  if query in character.name.lower() or 
                     (character.title and query in character.title.lower()) or
                     (character.description and query in character.description.lower())]
        
        return results
    
    def get_recent_characters(self, limit=3):
        """Obtiene los personajes más recientes (basado en OID)"""
        try:
            all_characters = self.get_all_characters()
            # Filtrar personajes que tengan OID válido
            characters_with_oid = [char for char in all_characters if hasattr(char, '_oid') and char._oid is not None]
            # Ordenar por OID (los más recientes tienen OID más alto)
            sorted_characters = sorted(characters_with_oid, key=lambda x: str(x._oid), reverse=True)
            return sorted_characters[:limit]
        except Exception as e:
            print(f"Error al obtener personajes recientes: {e}")
            return []
    
    def debug_characters(self):
        """Método de debug para inspeccionar los datos de personajes"""
        print("=== DEBUG: Inspeccionando personajes en la base de datos ===")
        try:
            count = 0
            for character in self.srp.load_all(Character):
                if character:
                    count += 1
                    print(f"Personaje {count}:")
                    print(f"  Nombre: {character.name}")
                    print(f"  Título: {character.title}")
                    print(f"  Estado: {character.status}")
                    print(f"  Descripción: {character.description[:50]}...")
                    print(f"  URL imagen: {character.image_url}")
                    print(f"  Casa ID: {character.house_id}")
                    print(f"  OID: {getattr(character, '_oid', 'None')}")
                    print("---")
            print(f"Total de personajes encontrados: {count}")
        except Exception as e:
            print(f"Error en debug: {e}")
        print("=== FIN DEBUG ===")
        return []