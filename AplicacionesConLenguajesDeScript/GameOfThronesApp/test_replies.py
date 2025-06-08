#!/usr/bin/env python3
"""
Script de diagnóstico para probar la funcionalidad de respuestas
"""

import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sirope-master'))

import sirope
from app.models.discussion import Discussion, DiscussionReply
from app.models.user import User

def test_reply_functionality():
    """Probar la funcionalidad básica de respuestas"""
    print("=== PRUEBA DE FUNCIONALIDAD DE RESPUESTAS ===\n")
    
    # Inicializar sirope
    repo = sirope.Sirope()
    
    try:
        # 1. Buscar una discusión existente
        discussions = list(repo.load_all(Discussion))
        if not discussions:
            print("❌ No hay discusiones en la base de datos")
            return False
            
        discussion = discussions[0]
        print(f"✅ Discusión encontrada: '{discussion.title}'")
        print(f"   - ID: {discussion.get_oid()}")
        print(f"   - Autor: {discussion.author_oid}")
        print(f"   - Respuestas actuales: {len(discussion.replies)}")
        
        # 2. Buscar un usuario existente
        users = list(repo.load_all(User))
        if not users:
            print("❌ No hay usuarios en la base de datos")
            return False
            
        user = users[0]
        print(f"✅ Usuario encontrado: '{user.username}'")
        print(f"   - ID: {user.__oid__}")
        
        # 3. Crear una respuesta de prueba
        test_content = f"Respuesta de prueba creada el {datetime.now()}"
        print(f"\n📝 Creando respuesta de prueba: '{test_content[:50]}...'")
        
        reply = DiscussionReply(test_content, user.__oid__, discussion.__oid__)
        print(f"✅ Objeto DiscussionReply creado")
        
        # 4. Guardar la respuesta
        reply_oid = repo.save(reply)
        print(f"✅ Respuesta guardada con ID: {reply_oid}")
        
        # 5. Agregar la respuesta a la discusión
        old_reply_count = len(discussion.replies)
        discussion.add_reply(reply_oid)
        repo.save(discussion)
        
        print(f"✅ Respuesta agregada a la discusión")
        print(f"   - Respuestas antes: {old_reply_count}")
        print(f"   - Respuestas después: {len(discussion.replies)}")
        
        # 6. Verificar que la respuesta se puede cargar
        loaded_reply = repo.load(reply_oid)
        if loaded_reply:
            print(f"✅ Respuesta cargada correctamente")
            print(f"   - Contenido: '{loaded_reply.content[:50]}...'")
            print(f"   - Autor: {loaded_reply.get_author_name(repo)}")
        else:
            print("❌ Error al cargar la respuesta")
            return False
            
        print(f"\n🎉 PRUEBA COMPLETADA EXITOSAMENTE")
        print(f"   - La funcionalidad de respuestas está funcionando")
        print(f"   - Total de respuestas en la discusión: {discussion.get_replies_count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database_status():
    """Verificar el estado de la base de datos"""
    print("=== VERIFICACIÓN DE BASE DE DATOS ===\n")
    
    repo = sirope.Sirope()
    
    try:
        # Contar objetos en la base de datos
        discussions = list(repo.load_all(Discussion))
        users = list(repo.load_all(User))
        replies = list(repo.load_all(DiscussionReply))
        
        print(f"📊 Estadísticas de la base de datos:")
        print(f"   - Discusiones: {len(discussions)}")
        print(f"   - Usuarios: {len(users)}")
        print(f"   - Respuestas: {len(replies)}")
        
        if discussions:
            print(f"\n📋 Discusiones encontradas:")
            for i, disc in enumerate(discussions[:3]):  # Solo mostrar las primeras 3
                print(f"   {i+1}. '{disc.title}' - {len(disc.replies)} respuestas")
                
        if replies:
            print(f"\n💬 Respuestas encontradas:")
            for i, reply in enumerate(replies[:5]):  # Solo mostrar las primeras 5
                print(f"   {i+1}. '{reply.content[:30]}...' - Autor: {reply.author_oid}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR verificando base de datos: {e}")
        return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO DE SISTEMA DE RESPUESTAS\n")
    
    # Verificar estado de la base de datos
    if not check_database_status():
        print("❌ Fallo en verificación de base de datos")
        sys.exit(1)
    
    print("\n" + "="*50 + "\n")
    
    # Probar funcionalidad de respuestas
    if not test_reply_functionality():
        print("❌ Fallo en prueba de funcionalidad")
        sys.exit(1)
    
    print(f"\n✅ DIAGNÓSTICO COMPLETADO - Todo funciona correctamente")