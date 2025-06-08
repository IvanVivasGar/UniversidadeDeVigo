#!/usr/bin/env python3
"""
WesterosTracker - Aplicación Flask para seguimiento de Game of Thrones
"""

from app import create_app
import os

# Crear aplicación Flask
app = create_app()

if __name__ == '__main__':
    # Crear directorio de uploads si no existe
    upload_dir = os.path.join('app', 'static', 'images', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Crear subdirectorios para cada tipo de entidad
    for folder in ['characters', 'houses', 'events', 'discussions', 'general']:
        entity_dir = os.path.join(upload_dir, folder)
        os.makedirs(entity_dir, exist_ok=True)
    
    # Ejecutar aplicación en modo debug
    app.run(debug=True, host='0.0.0.0', port=3000)