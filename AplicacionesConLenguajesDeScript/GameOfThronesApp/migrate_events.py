#!/usr/bin/env python3
"""
Script de migración para actualizar eventos existentes al nuevo formato con user_ratings
"""

import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sirope-master'))
import sirope

from app.models.event import Event

def migrate_events():
    """Migrar eventos existentes al nuevo formato"""
    print("Iniciando migración de eventos...")
    
    # Crear instancia de sirope
    sirope_instance = sirope.Sirope()
    
    try:
        # Cargar todos los eventos
        events = list(sirope_instance.load_all(Event))
        print(f"Encontrados {len(events)} eventos para migrar")
        
        migrated_count = 0
        
        for event in events:
            needs_migration = False
            
            # Verificar si el evento necesita migración
            if not hasattr(event, 'user_ratings'):
                event.user_ratings = {}
                needs_migration = True
                print(f"Agregando user_ratings a evento: {event.name}")
            
            # Migrar ratings antiguos si existen
            if hasattr(event, 'ratings') and event.ratings:
                if not event.user_ratings:  # Solo migrar si user_ratings está vacío
                    # Crear ratings ficticios para mantener compatibilidad
                    for i, rating in enumerate(event.ratings[:5]):  # Máximo 5 ratings
                        fake_user_id = f"migrated_user_{i}"
                        event.user_ratings[fake_user_id] = rating
                    print(f"Migrados {len(event.ratings)} ratings antiguos para: {event.name}")
                    needs_migration = True
            
            # Asegurar que los campos requeridos existen
            if not hasattr(event, 'rating_count'):
                event.rating_count = len(event.user_ratings) if hasattr(event, 'user_ratings') else 0
                needs_migration = True
            
            if not hasattr(event, 'total_rating'):
                if hasattr(event, 'user_ratings') and event.user_ratings:
                    ratings_list = list(event.user_ratings.values())
                    event.total_rating = sum(ratings_list) / len(ratings_list)
                else:
                    event.total_rating = 0.0
                needs_migration = True
            
            # Guardar si se hicieron cambios
            if needs_migration:
                sirope_instance.save(event)
                migrated_count += 1
                print(f"✓ Evento migrado: {event.name}")
        
        print(f"\nMigración completada. {migrated_count} eventos actualizados.")
        
    except Exception as e:
        print(f"Error durante la migración: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = migrate_events()
    if success:
        print("¡Migración completada exitosamente!")
    else:
        print("La migración falló. Revisa los errores arriba.")
        sys.exit(1)