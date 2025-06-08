# WesterosTracker - Documentación del Proyecto

## 1. Introducción

WesterosTracker es una aplicación web desarrollada en Flask que permite gestionar y hacer seguimiento de información relacionada con Game of Thrones. La aplicación implementa un sistema completo de gestión de personajes, casas nobles, eventos, y un foro de discusión con sistema de autenticación.

## 2. Arquitectura del Sistema

### 2.1 Tecnologías Utilizadas
- **Backend**: Flask (Python)
- **Base de Datos**: Redis con ORM Sirope
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Autenticación**: Flask-Login
- **Estilos**: CSS personalizado con temática épica

### 2.2 Estructura del Proyecto
```
WesterosTracker/
├── app/
│   ├── models/          # Modelos de datos (User, Character, House, Event, Post)
│   ├── routes/          # Blueprints de rutas organizados por funcionalidad
│   ├── templates/       # Plantillas HTML con herencia
│   ├── static/          # Archivos CSS, JS e imágenes
│   └── utils/           # Funciones auxiliares
├── sirope-master/       # ORM personalizado para Redis
├── config.py           # Configuración de la aplicación
├── app.py              # Punto de entrada principal
└── requirements.txt    # Dependencias del proyecto
```

## 3. Funcionalidades Implementadas

### 3.1 Sistema de Autenticación
- Registro de usuarios con validación épica
- Login/logout con sesiones seguras
- Hash de contraseñas con werkzeug.security
- Perfiles de usuario editables

### 3.2 Gestión de Personajes
- CRUD completo de personajes
- Estados: Vivo, Muerto, Desconocido
- Afiliación a casas nobles
- Sistema de calificaciones (1-5 estrellas)
- Upload de imágenes

### 3.3 Gestión de Casas Nobles
- Creación y edición de casas
- Lemas y descripciones
- Múltiples imágenes por casa
- Listado de miembros
- Sistema de rating

### 3.4 Gestión de Eventos
- Eventos organizados por temporada y episodio
- Descripciones detalladas
- Fechas de emisión
- Calificaciones comunitarias

### 3.5 Sistema de Posts/Foros
- Creación de posts con contenido rich
- Sistema de likes
- Comentarios anidados
- Moderación básica

### 3.6 Panel de Administración
- Gestión de usuarios
- Moderación de contenido
- Estadísticas del sistema

## 4. Modelos de Datos

### 4.1 User
```python
class User:
    - username: str (único)
    - email: str (único)
    - password_hash: str
    - is_admin: bool
    - created_at: datetime
```

### 4.2 Character
```python
class Character:
    - name: str
    - description: str
    - house: str (referencia a House)
    - status: str (alive/dead/unknown)
    - image_path: str
    - ratings: list[Rating]
```

### 4.3 House
```python
class House:
    - name: str
    - motto: str
    - description: str
    - images: list[str]
    - members: list[Character]
    - ratings: list[Rating]
```

### 4.4 Event
```python
class Event:
    - title: str
    - description: str
    - season: int
    - episode: int
    - air_date: datetime
    - ratings: list[Rating]
```

## 5. Patrones de Diseño Implementados

### 5.1 Blueprint Pattern
La aplicación utiliza Flask Blueprints para organizar las rutas:
- auth: Autenticación
- main: Página principal
- characters: Gestión de personajes
- houses: Gestión de casas
- events: Gestión de eventos
- posts: Sistema de foros

### 5.2 Template Inheritance
Todas las plantillas extienden de `base.html` que incluye:
- Estructura HTML común
- Navigation bar
- Footer
- Scripts comunes

### 5.3 Repository Pattern
Los modelos implementan métodos estáticos para operaciones CRUD:
- `get_all()`
- `get_by_id()`
- `save()`
- `delete()`

## 6. Seguridad Implementada

### 6.1 Autenticación
- Hash de contraseñas con salt
- Sesiones seguras con Flask-Login
- Protección de rutas con decoradores

### 6.2 Validación de Datos
- Validación client-side con JavaScript
- Validación server-side en Flask
- Sanitización de inputs

### 6.3 Upload de Archivos
- Validación de tipos de archivo
- Límites de tamaño
- Nombres seguros para archivos

## 7. Interfaz de Usuario

### 7.1 Diseño Temático
- Estilo épico inspirado en Game of Thrones
- Colores dorados y oscuros
- Efectos visuales con CSS3
- Animaciones suaves

### 7.2 Responsividad
- Diseño adaptable a diferentes pantallas
- Mobile-first approach
- Flexbox y Grid CSS

### 7.3 Interactividad
- JavaScript vanilla para efectos
- AJAX para operaciones sin recarga
- Notificaciones toast personalizadas

## 8. Instalación y Configuración

### 8.1 Prerrequisitos
- Python 3.8+
- Redis Server
- pip (gestor de paquetes Python)

### 8.2 Pasos de Instalación
1. Clonar el repositorio
2. Instalar Redis: `brew install redis` (macOS)
3. Instalar dependencias: `pip install -r requirements.txt`
4. Iniciar Redis: `brew services start redis`
5. Ejecutar aplicación: `python app.py`
6. Acceder a: `http://localhost:3000`

## 9. Pruebas y Calidad

### 9.1 Pruebas Implementadas
- Pruebas unitarias para modelos
- Pruebas de integración para rutas
- Validación de formularios

### 9.2 Estándares de Código
- PEP 8 para Python
- Comentarios descriptivos
- Estructura modular

## 10. Conclusiones

WesterosTracker representa una aplicación web completa que demuestra:
- Arquitectura MVC bien estructurada
- Implementación de patrones de diseño
- Interfaz de usuario atractiva y funcional
- Sistema de gestión de datos robusto
- Medidas de seguridad apropiadas

La aplicación está lista para uso en entorno de desarrollo y puede ser extendida con funcionalidades adicionales según las necesidades del proyecto.