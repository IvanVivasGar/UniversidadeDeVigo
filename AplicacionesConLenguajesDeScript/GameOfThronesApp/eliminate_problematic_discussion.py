#!/usr/bin/env python3
"""
Script para eliminar definitivamente discusiones problemáticas
que tienen problemas con el atributo namespace de sirope
VERSIÓN MEJORADA - Maneja discusiones con namespace corrupto
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sirope-master'))

import sirope
import redis
from app.models.discussion import Discussion
from app.models.post import Post

def eliminate_all_problematic_discussions_v2():
    """Eliminar TODAS las discusiones con manejo robusto de errores de namespace"""
    print("🎯 Iniciando eliminación masiva MEJORADA de discusiones problemáticas")
    
    # Conectar a Redis y Sirope
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    s = sirope.Sirope(redis_client)
    
    try:
        # Paso 1: Intentar cargar discusiones con manejo de errores
        print("📋 Cargando discusiones con manejo robusto de errores...")
        discussions = []
        discussion_oids = []
        
        try:
            # Cargar discusiones normalmente
            discussions = list(s.load_all(Discussion))
            print(f"📊 Discusiones cargadas normalmente: {len(discussions)}")
        except Exception as e:
            print(f"⚠️ Error cargando discusiones normalmente: {e}")
            
            # Método alternativo: buscar directamente en Redis
            print("🔧 Intentando método alternativo desde Redis...")
            discussion_oids = _find_discussion_oids_in_redis(redis_client)
            print(f"📊 OIDs de discusiones encontrados en Redis: {len(discussion_oids)}")
        
        # Paso 2: Eliminar todos los posts relacionados
        print("🧹 Eliminando todos los posts de discusiones...")
        posts_deleted = 0
        
        try:
            all_posts = list(s.load_all(Post))
            for post in all_posts:
                if hasattr(post, 'discussion_oid'):
                    try:
                        _force_delete_from_redis(redis_client, str(post.__oid__))
                        posts_deleted += 1
                    except Exception as e:
                        print(f"⚠️ Error eliminando post: {e}")
        except Exception as e:
            print(f"⚠️ Error cargando posts: {e}")
        
        print(f"✅ {posts_deleted} posts eliminados")
        
        # Paso 3: Eliminar discusiones cargadas normalmente
        if discussions:
            print("🗑️ Eliminando discusiones cargadas normalmente...")
            for disc in discussions:
                try:
                    _force_delete_from_redis(redis_client, str(disc.__oid__))
                except Exception as e:
                    print(f"⚠️ Error eliminando discusión {getattr(disc, 'title', 'sin título')}: {e}")
        
        # Paso 4: Eliminar discusiones encontradas en Redis directamente
        if discussion_oids:
            print("🗑️ Eliminando discusiones encontradas en Redis...")
            for oid in discussion_oids:
                try:
                    _force_delete_from_redis(redis_client, oid)
                except Exception as e:
                    print(f"⚠️ Error eliminando OID {oid}: {e}")
        
        # Paso 5: Limpieza profunda de colecciones
        print("🧽 Realizando limpieza profunda de colecciones...")
        _deep_clean_discussions(redis_client)
        
        # Paso 6: Verificación final
        print("🔍 Verificando eliminación completa...")
        try:
            final_discussions = list(s.load_all(Discussion))
            final_count = len(final_discussions)
        except Exception as e:
            print(f"⚠️ Error verificando discusiones finales: {e}")
            # Verificar directamente en Redis
            final_oids = _find_discussion_oids_in_redis(redis_client)
            final_count = len(final_oids)
        
        if final_count == 0:
            print("✅ ¡TODAS las discusiones eliminadas exitosamente!")
            print("📊 Discusiones restantes: 0")
            return True
        else:
            print(f"⚠️ Aún quedan {final_count} discusiones")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la eliminación masiva: {e}")
        import traceback
        traceback.print_exc()
        return False

def _find_discussion_oids_in_redis(redis_client):
    """Encontrar OIDs de discusiones directamente en Redis"""
    discussion_oids = []
    try:
        # Buscar keys que contengan "Discussion"
        pattern = "*Discussion*"
        keys = list(redis_client.scan_iter(match=pattern))
        
        for key in keys:
            key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
            
            # Extraer OIDs de las keys
            if '@' in key_str:
                parts = key_str.split('@')
                if len(parts) >= 2:
                    oid_part = '@'.join(parts[1:])  # Todo después del primer @
                    if oid_part not in discussion_oids:
                        discussion_oids.append(oid_part)
        
        print(f"🔍 Encontrados {len(discussion_oids)} OIDs únicos de discusiones")
        
    except Exception as e:
        print(f"Error buscando OIDs en Redis: {e}")
    
    return discussion_oids

def _deep_clean_discussions(redis_client):
    """Limpieza profunda de todas las referencias a discusiones"""
    try:
        # Patrones para buscar keys relacionadas con discusiones
        patterns = [
            "*Discussion*",
            "*DiscussionReply*", 
            "*discussion*",
            "*post*Discussion*"
        ]
        
        total_deleted = 0
        
        for pattern in patterns:
            keys_to_delete = list(redis_client.scan_iter(match=pattern))
            if keys_to_delete:
                redis_client.delete(*keys_to_delete)
                deleted_count = len(keys_to_delete)
                total_deleted += deleted_count
                print(f"🧽 Eliminadas {deleted_count} keys con patrón '{pattern}'")
        
        print(f"✅ Total keys eliminadas en limpieza profunda: {total_deleted}")
        
    except Exception as e:
        print(f"Error en limpieza profunda: {e}")

def _force_delete_from_redis(redis_client, oid_str):
    """Eliminar todas las keys relacionadas con un OID desde Redis"""
    keys_deleted = 0
    try:
        # Buscar todas las keys que contengan el OID
        all_keys = redis_client.keys('*')
        keys_to_delete = []
        
        for key in all_keys:
            key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
            if oid_str in key_str:
                keys_to_delete.append(key)
        
        # Eliminar las keys encontradas
        if keys_to_delete:
            redis_client.delete(*keys_to_delete)
            keys_deleted = len(keys_to_delete)
            
    except Exception as e:
        print(f"Error eliminando keys de Redis: {e}")
    
    return keys_deleted

def test_discussion_loading():
    """Probar si se pueden cargar discusiones sin errores"""
    print("🧪 Probando carga de discusiones...")
    
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    s = sirope.Sirope(redis_client)
    
    try:
        discussions = list(s.load_all(Discussion))
        print(f"✅ Carga exitosa: {len(discussions)} discusiones")
        
        for disc in discussions:
            try:
                # Probar acceso a atributos básicos
                title = getattr(disc, 'title', 'Sin título')
                content = getattr(disc, 'content', 'Sin contenido')
                oid = str(disc.__oid__)
                print(f"   - {title} ({oid})")
            except Exception as e:
                print(f"   ❌ Error en discusión: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando discusiones: {e}")
        return False

if __name__ == "__main__":
    print("🛠️ SCRIPT DE ELIMINACIÓN MEJORADO DE DISCUSIONES PROBLEMÁTICAS")
    print("=" * 70)
    
    # Primero probar si podemos cargar discusiones
    print("\n1️⃣ PRUEBA DE CARGA:")
    can_load = test_discussion_loading()
    
    print("\n2️⃣ ELIMINACIÓN MASIVA:")
    success = eliminate_all_problematic_discussions_v2()
    
    print("\n3️⃣ VERIFICACIÓN FINAL:")
    final_test = test_discussion_loading()
    
    if success and final_test:
        print("\n🎉 ¡MISIÓN CUMPLIDA! TODAS las discusiones problemáticas han sido eliminadas.")
        print("🎨 Ahora puedes crear nuevas discusiones sin problemas.")
        print("💡 IMPORTANTE: Reinicia la aplicación Flask para limpiar la caché.")
    else:
        print("\n😞 La eliminación no fue completamente exitosa.")
        print("🔧 Puede ser necesario reiniciar Redis y la aplicación.")
        print("📋 Revisa los logs para más detalles.")