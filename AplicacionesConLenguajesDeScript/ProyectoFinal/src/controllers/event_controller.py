import sirope
from models.event import Event

class EventController:
    def __init__(self, srp: sirope.Sirope):
        self.srp = srp

    def create_event(self, name, season, episode, description, location, importance, image_url=None):
        """Crea un nuevo evento"""
        event = Event(name, season, episode, description, location, importance, image_url)
        # Guardar y obtener el OID asignado por Sirope
        event._oid = self.srp.save(event)
        return event

    def get_all_events(self):
        """Obtiene todos los eventos"""
        events = []
        try:
            # Usar load_all en lugar de filter
            for event in self.srp.load_all(Event):
                if event:
                    events.append(event)
        except Exception as e:
            print(f"Error al cargar eventos: {e}")
        return events

    def get_event_by_id(self, event_id):
        """Obtiene un evento por su ID"""
        if not event_id:
            return None
            
        try:
            from sirope.oid import OID
            # Si es una cadena, intenta convertirla a OID
            if isinstance(event_id, str):
                # Verificar si ya tiene el formato correcto para OID
                if '@' in event_id:
                    # Extraer solo el número después del @ si es una representación como "models.event.Event@3"
                    parts = event_id.split('@')
                    if len(parts) > 1:
                        event_id = parts[1]
                event_id = OID(event_id)
            
            event = self.srp.load(event_id)
            return event
        except Exception as e:
            print(f"Error al cargar evento (ID: {event_id}): {e}")
            return None

    def get_events_by_season(self, season):
        """Obtiene todos los eventos de una temporada específica"""
        events = []
        try:
            for event in self.srp.load_all(Event):
                if event and hasattr(event, '_season') and event._season == season:
                    events.append(event)
        except Exception as e:
            print(f"Error al cargar eventos por temporada: {e}")
        return events

    def update_event(self, event_id, name, season, episode, description, location, importance, image_url=None):
        """Actualiza un evento existente"""
        event = self.srp.load(event_id)
        if event:
            event._name = name
            event._season = season
            event._episode = episode
            event._description = description
            event._location = location
            event._importance = importance
            if image_url:
                event._image_url = image_url
            self.srp.save(event)
            return True, "Evento actualizado correctamente"
        return False, "Evento no encontrado"

    def delete_event(self, event_id):
        """Elimina un evento"""
        event = self.srp.load(event_id)
        if event:
            self.srp.delete(event)
            return True, "Evento eliminado correctamente"
        return False, "Evento no encontrado"
    
    def add_related_character(self, event_id, character_id):
        """Añade un personaje relacionado al evento"""
        event = self.srp.load(event_id)
        if event and event.add_related_character(character_id):
            self.srp.save(event)
            return True, "Personaje relacionado añadido correctamente"
        return False, "No se pudo añadir el personaje relacionado"
    
    def remove_related_character(self, event_id, character_id):
        """Elimina un personaje relacionado del evento"""
        event = self.srp.load(event_id)
        if event and event.remove_related_character(character_id):
            self.srp.save(event)
            return True, "Personaje relacionado eliminado correctamente"
        return False, "No se pudo eliminar el personaje relacionado"
    
    def add_related_house(self, event_id, house_id):
        """Añade una casa relacionada al evento"""
        event = self.srp.load(event_id)
        if event and event.add_related_house(house_id):
            self.srp.save(event)
            return True, "Casa relacionada añadida correctamente"
        return False, "No se pudo añadir la casa relacionada"
    
    def remove_related_house(self, event_id, house_id):
        """Elimina una casa relacionada del evento"""
        event = self.srp.load(event_id)
        if event and event.remove_related_house(house_id):
            self.srp.save(event)
            return True, "Casa relacionada eliminada correctamente"
        return False, "No se pudo eliminar la casa relacionada"
    
    def add_comment(self, event_id, user_id, text):
        """Añade un comentario al evento"""
        event = self.srp.load(event_id)
        if event and event.add_comment(user_id, text):
            self.srp.save(event)
            return True, "Comentario añadido correctamente"
        return False, "No se pudo añadir el comentario"
    
    def get_recent_events(self, limit=3):
        """Obtiene los eventos más recientes (basado en OID)"""
        try:
            all_events = self.get_all_events()
            # Filtrar eventos que tengan OID válido
            events_with_oid = [event for event in all_events if hasattr(event, '_oid') and event._oid is not None]
            # Ordenar por OID (los más recientes tienen OID más alto)
            sorted_events = sorted(events_with_oid, key=lambda x: str(x._oid), reverse=True)
            return sorted_events[:limit]
        except Exception as e:
            print(f"Error al obtener eventos recientes: {e}")
            return []