#!/bin/bash

# Script para generar la entrega del proyecto según los requisitos académicos
# Uso: ./generar_entrega.sh APELLIDO1_APELLIDO2_NOMBRE DNI

if [ $# -ne 2 ]; then
    echo "Uso: $0 APELLIDO1_APELLIDO2_NOMBRE DNI"
    echo "Ejemplo: $0 garcia_lopez_juan 12345678A"
    exit 1
fi

NOMBRE_ESTUDIANTE=$1
DNI=$2
NOMBRE_ARCHIVO="ALS-proyecto-${NOMBRE_ESTUDIANTE}-${DNI}"

echo "🏰 Generando entrega para: $NOMBRE_ESTUDIANTE (DNI: $DNI)"
echo "📦 Nombre del archivo: ${NOMBRE_ARCHIVO}.zip"

# Crear estructura de entrega
echo "📁 Creando estructura de entrega..."
rm -rf "${NOMBRE_ARCHIVO}"
mkdir -p "${NOMBRE_ARCHIVO}/src"
mkdir -p "${NOMBRE_ARCHIVO}/doc"

# Copiar código fuente
echo "📋 Copiando código fuente..."
cp -r app/ "${NOMBRE_ARCHIVO}/src/"
cp app.py config.py requirements.txt README.md "${NOMBRE_ARCHIVO}/src/"
cp -r sirope-master/ "${NOMBRE_ARCHIVO}/src/"

# Actualizar info.txt con datos reales
echo "📝 Actualizando archivo info.txt..."
cat > "${NOMBRE_ARCHIVO}/doc/info.txt" << EOF
Título del proyecto: WesterosTracker - Aplicación Web Game of Thrones
URL del proyecto: http://localhost:3000 (aplicación web local Flask)
Apellidos y nombre: ${NOMBRE_ESTUDIANTE//_/ }
DNI: ${DNI}

Descripción:
Aplicación web Flask para el seguimiento y gestión de información sobre Game of Thrones.
Incluye gestión de personajes, casas nobles, eventos, sistema de posts/foros, 
autenticación de usuarios y sistema de calificaciones.

Tecnologías utilizadas:
- Backend: Flask, Flask-Login
- Base de Datos: Redis + Sirope (ORM)
- Frontend: HTML5, CSS3, JavaScript
- Autenticación: Flask-Login con hashing de contraseñas

Instrucciones de ejecución:
1. Instalar Redis: brew install redis && brew services start redis
2. Instalar dependencias: pip install -r requirements.txt
3. Ejecutar: python app.py
4. Acceder a: http://localhost:3000

Repositorio Git: [INDICA_AQUÍ_TU_REPOSITORIO_GIT]
EOF

# Copiar documentación
echo "📚 Copiando documentación..."
cp entrega_proyecto/doc/documentacion.md "${NOMBRE_ARCHIVO}/doc/"

# Crear el ZIP
echo "🗜️ Creando archivo ZIP..."
zip -r "${NOMBRE_ARCHIVO}.zip" "${NOMBRE_ARCHIVO}/"

# Limpiar directorio temporal
rm -rf "${NOMBRE_ARCHIVO}"

echo "✅ ¡Entrega generada exitosamente!"
echo "📦 Archivo creado: ${NOMBRE_ARCHIVO}.zip"
echo ""
echo "📋 Pasos siguientes:"
echo "1. Convertir doc/documentacion.md a PDF"
echo "2. Añadir el PDF al ZIP"
echo "3. Actualizar la URL del repositorio Git en info.txt"
echo "4. Subir a la plataforma de docencia con asunto: ${NOMBRE_ARCHIVO}"
echo ""
echo "🏰 ¡Que los Antiguos Dioses y los Nuevos te acompañen en tu entrega!"