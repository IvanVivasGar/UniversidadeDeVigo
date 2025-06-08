#!/usr/bin/env python3
"""
Script para migrar usuarios existentes y crear un administrador.
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User
import hashlib

def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    """Función principal para migrar usuarios y crear administrador"""
    app = create_app()
    
    with app.app_context():
        # Obtener sirope desde la aplicación
        sirope = app.sirope
        
        if sirope is None:
            print("❌ Error: No se pudo conectar con Redis/Sirope")
            return
        
        print("🔧 Iniciando migración de usuarios...")
        
        # Obtener todos los usuarios existentes
        users = list(sirope.load_all(User))
        print(f"📊 Encontrados {len(users)} usuarios existentes")
        
        # Migrar usuarios existentes
        migrated_count = 0
        for user in users:
            if not hasattr(user, 'is_admin'):
                user.is_admin = False
                sirope.save(user)
                migrated_count += 1
                print(f"✅ Usuario '{user.username}' migrado con is_admin=False")
        
        print(f"🔄 Migrados {migrated_count} usuarios existentes")
        
        # Crear usuario administrador si no existe
        admin_username = "admin"
        admin_email = "admin@westeros.com"
        admin_password = "admin123"  # Cambia esto por una contraseña segura
        
        # Verificar si ya existe un administrador
        existing_admin = None
        for user in users:
            if hasattr(user, 'is_admin') and user.is_admin:
                existing_admin = user
                break
        
        if existing_admin:
            print(f"👑 Ya existe un administrador: {existing_admin.username}")
        else:
            # Verificar si existe usuario con username 'admin'
            admin_user = None
            for user in users:
                if user.username == admin_username:
                    admin_user = user
                    break
            
            if admin_user:
                # Convertir usuario existente en administrador
                admin_user.is_admin = True
                sirope.save(admin_user)
                print(f"👑 Usuario '{admin_username}' convertido en administrador")
            else:
                # Crear nuevo usuario administrador
                new_admin = User(username=admin_username, email=admin_email)
                new_admin.set_password(admin_password)
                new_admin.is_admin = True
                
                # Guardar en sirope
                sirope.save(new_admin)
                print(f"👑 Nuevo administrador creado:")
                print(f"   Username: {admin_username}")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                print(f"   ⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
        print("\n🎉 Migración completada exitosamente!")
        print(f"💡 Credenciales de administrador:")
        print(f"   Username: {admin_username}")
        print(f"   Password: {admin_password}")
        print(f"   🔐 Los botones de administración aparecerán automáticamente")

if __name__ == "__main__":
    main()