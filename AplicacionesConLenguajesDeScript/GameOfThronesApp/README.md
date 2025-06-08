# WesterosTracker

Aplicación web Flask para el seguimiento y gestión de información sobre Game of Thrones.

## Características

- **Gestión de Personajes**: Crear, editar y calificar personajes
- **Gestión de Casas**: Administrar casas nobles con múltiples imágenes
- **Gestión de Eventos**: Seguimiento de eventos por temporada y episodio
- **Sistema de Posts**: Foro de discusión con likes y comentarios
- **Sistema de Ratings**: Calificación de 1-5 estrellas para todas las entidades
- **Autenticación de Usuarios**: Registro, login y perfiles de usuario
- **Upload de Imágenes**: Soporte para múltiples imágenes por entidad

## Tecnologías Utilizadas

- **Backend**: Flask, Flask-Login
- **Base de Datos**: Redis + Sirope (ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticación**: Flask-Login con hashing de contraseñas

## Instalación

1. Instalar Redis:
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecutar la aplicación:
```bash
python app.py
```

## Estructura del Proyecto

```
WesterosTracker/
├── app/
│   ├── models/          # Modelos de datos
│   ├── routes/          # Blueprints de rutas
│   ├── templates/       # Plantillas HTML
│   ├── static/          # Archivos estáticos
│   └── utils/           # Utilidades helper
├── sirope-master/       # ORM Sirope
├── config.py           # Configuración
├── app.py              # Punto de entrada
└── requirements.txt    # Dependencias
```

## Uso

1. Acceder a `http://localhost:5000`
2. Registrarse o iniciar sesión
3. Explorar personajes, casas y eventos
4. Crear posts y participar en discusiones
5. Calificar contenido y subir imágenes

## Modelos de Datos

- **User**: Usuarios con autenticación
- **Character**: Personajes con estado y afiliación
- **House**: Casas nobles con lemas y miembros
- **Event**: Eventos con temporada/episodio
- **Post/Comment**: Sistema de foro social