from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_required
import sirope
import os
from werkzeug.security import generate_password_hash
import datetime

# Importando modelos
from models.user import User
from models.character import Character
from models.house import House
from models.event import Event

# Importando controladores
from controllers.auth_controller import AuthController
from controllers.character_controller import CharacterController
from controllers.house_controller import HouseController
from controllers.event_controller import EventController

# Importando rutas
from routes.auth_routes import auth_bp
from routes.character_routes import character_bp
from routes.house_routes import house_bp
from routes.event_routes import event_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'clave-secreta-por-defecto')
app.config['SIROPE_PATH'] = os.path.join(os.path.dirname(__file__), 'db')

# Configuración mejorada de sesiones
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)  # 7 días de duración
app.config['REMEMBER_COOKIE_DURATION'] = datetime.timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = False  # Cambiar a True en producción con HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Inicializar Sirope (base de datos orientada a objetos)
srp = sirope.Sirope()

# Inicializar controladores
auth_controller = AuthController(srp)
character_controller = CharacterController(srp)
house_controller = HouseController(srp)
event_controller = EventController(srp)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Carga un usuario desde la base de datos por su ID"""
    from sirope.oid import OID
    # Verificar si user_id es una cadena y convertirla a OID si es necesario
    if isinstance(user_id, str):
        try:
            # Intentar cargar el usuario por su nombre de usuario
            for user in srp.load_all(User):
                if str(user.get_id()) == user_id:
                    return user
            return None
        except Exception as e:
            print(f"Error al cargar usuario: {e}")
            return None
    # Si es un OID, usarlo directamente
    return srp.load(user_id)

# Registrar blueprints (rutas)
app.register_blueprint(auth_bp)
app.register_blueprint(character_bp)
app.register_blueprint(house_bp)
app.register_blueprint(event_bp)

# Rutas principales
@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Panel de control para usuarios autenticados"""
    # Obtener estadísticas básicas
    total_characters = len(list(srp.load_all(Character)))
    total_houses = len(list(srp.load_all(House)))
    total_events = len(list(srp.load_all(Event)))
    
    stats = {
        'characters': total_characters,
        'houses': total_houses,
        'events': total_events
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/search')
def search():
    """Página de búsqueda"""
    query = request.args.get('q', '')
    results = []
    
    if query:
        # Buscar en personajes
        characters = srp.load_all(Character)
        for character in characters:
            if query.lower() in character.name.lower() or query.lower() in character.description.lower():
                results.append({
                    'type': 'character',
                    'name': character.name,
                    'description': character.description,
                    'url': url_for('characters.character_detail', character_id=str(character._oid))
                })
        
        # Buscar en casas
        houses = srp.load_all(House)
        for house in houses:
            if query.lower() in house.name.lower() or query.lower() in house.description.lower():
                results.append({
                    'type': 'house',
                    'name': house.name,
                    'description': house.description,
                    'url': url_for('houses.house_detail', house_id=str(house._oid))
                })
    
    return render_template('search.html', query=query, results=results)

@app.route('/debug/characters')
def debug_characters():
    """Ruta temporal para debug de personajes"""
    character_controller.debug_characters()
    return "Debug ejecutado. Revisa la consola del servidor."

@app.route('/debug/full-reset')
def full_reset():
    """Reseteo completo de la base de datos - FUNCIÓN ÚNICA DE RESET"""
    try:
        import shutil
        import os
        
        # Obtener la ruta de la base de datos
        db_path = os.path.join(os.path.dirname(__file__), 'db')
        
        print("DEBUG: Eliminando completamente la base de datos...")
        
        # Eliminar completamente el directorio de la base de datos
        if os.path.exists(db_path):
            shutil.rmtree(db_path)
            print("DEBUG: Base de datos eliminada")
        
        # Recrear el directorio
        os.makedirs(db_path, exist_ok=True)
        
        # Crear una nueva instancia de Sirope
        global srp, character_controller, house_controller, event_controller
        srp = sirope.Sirope()
        
        # Recrear controladores
        character_controller = CharacterController(srp)
        house_controller = HouseController(srp)
        event_controller = EventController(srp)
        
        print("DEBUG: Recreando datos limpios...")
        
        # Crear casas con datos correctos
        house_stark = House(
            name="Casa Stark",
            words="Winter is Coming",
            region="El Norte",
            lord="Jon Snow",
            description="Una de las Grandes Casas de Westeros, conocida por su honor y lealtad.",
            image_url="https://images.ctfassets.net/usf1vwtuqyxm/stark/stark-banner.jpg"
        )
        
        house_lannister = House(
            name="Casa Lannister", 
            words="Hear Me Roar",
            region="Las Tierras del Oeste",
            lord="Tyrion Lannister",
            description="La casa más rica de Westeros, conocida por su astucia y riqueza.",
            image_url="https://images.ctfassets.net/usf1vwtuqyxm/lannister/lannister-banner.jpg"
        )
        
        house_targaryen = House(
            name="Casa Targaryen",
            words="Fire and Blood", 
            region="Tierras de la Corona",
            lord="Daenerys Targaryen",
            description="Antigua casa real de Westeros, señores de los dragones.",
            image_url="https://images.ctfassets.net/usf1vwtuqyxm/targaryen/targaryen-banner.jpg"
        )
        
        # Guardar casas
        house_stark._oid = srp.save(house_stark)
        house_lannister._oid = srp.save(house_lannister)
        house_targaryen._oid = srp.save(house_targaryen)
        
        # Crear personajes con datos correctos
        jon_snow = Character(
            name="Jon Snow",
            title="Rey en el Norte",
            description="Bastardo de Ned Stark, convertido en Rey en el Norte tras la Batalla de los Bastardos.",
            image_url="https://images.ctfassets.net/usf1vwtuqyxm/2v0bZhVGe4MWeSY3e2Jcas/6e5c3c5b7e1a4b8c9d0e1f2g3h4i5j6k/jon-snow.jpg",
            status="Alive",
            house_id=house_stark._oid
        )
        
        tyrion_lannister = Character(
            name="Tyrion Lannister",
            title="Mano de la Reina", 
            description="El Gnomo, hermano menor de Cersei y Jaime, conocido por su inteligencia.",
            image_url="https://images.ctfassets.net/usf1vwtuqyxm/tyrion/tyrion-lannister.jpg",
            status="Alive",
            house_id=house_lannister._oid
        )
        
        daenerys_targaryen = Character(
            name="Daenerys Targaryen",
            title="Madre de Dragones",
            description="La última Targaryen, conquistadora de Essos y pretendiente al Trono de Hierro.",
            image_url="https://images.ctfassets.net/usf1vwtuqyxm/daenerys/daenerys-targaryen.jpg",
            status="Dead",
            house_id=house_targaryen._oid
        )
        
        arya_stark = Character(
            name="Arya Stark",
            title="Asesina sin Rostro",
            description="Hija menor de Ned Stark, entrenada como asesina sin rostro.",
            image_url="https://images.ctfassets.net/usf1vwtuqyxm/arya/arya-stark.jpg",
            status="Alive",
            house_id=house_stark._oid
        )
        
        # Guardar personajes
        jon_snow._oid = srp.save(jon_snow)
        tyrion_lannister._oid = srp.save(tyrion_lannister)
        daenerys_targaryen._oid = srp.save(daenerys_targaryen)
        arya_stark._oid = srp.save(arya_stark)
        
        print("DEBUG: Reset completo exitoso!")
        return "Base de datos completamente reseteada y recreada. Verifica /characters/"
        
    except Exception as e:
        print(f"Error en reset completo: {e}")
        return f"Error: {e}"

# Manejadores de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

def initialize_sample_data():
    """Inicializar datos de ejemplo si no existen"""
    try:
        # Verificar si ya hay datos
        existing_houses = list(srp.load_all(House))
        existing_characters = list(srp.load_all(Character))
        existing_events = list(srp.load_all(Event))
        
        if existing_houses or existing_characters or existing_events:
            print("DEBUG: Ya existen datos en la base de datos")
            return
        
        print("DEBUG: Datos de ejemplo deshabilitados temporalmente")
        # Función temporalmente deshabilitada para evitar datos corruptos
        return
        
        print("DEBUG: Inicializando datos de ejemplo...")
        
        # Crear casas
        house_stark = House(
            name="Casa Stark",
            motto="Winter is Coming",
            seat="Winterfell",
            region="El Norte",
            lord="Jon Snow",
            description="Una de las Grandes Casas de Westeros, conocida por su honor y lealtad."
        )
        
        house_lannister = House(
            name="Casa Lannister",
            motto="Hear Me Roar",
            seat="Roca Casterly",
            region="Las Tierras del Oeste",
            lord="Tyrion Lannister",
            description="La casa más rica de Westeros, conocida por su astucia y riqueza."
        )
        
        house_targaryen = House(
            name="Casa Targaryen",
            motto="Fire and Blood",
            seat="Rocadragón",
            region="Tierras de la Corona",
            lord="Daenerys Targaryen",
            description="Antigua casa real de Westeros, señores de los dragones."
        )
        
        # Guardar casas
        srp.save(house_stark)
        srp.save(house_lannister)
        srp.save(house_targaryen)
        
        # Crear personajes
        jon_snow = Character(
            name="Jon Snow",
            title="Rey en el Norte",
            house_id=house_stark._oid,
            status="Alive",
            description="Bastardo de Ned Stark, convertido en Rey en el Norte tras la Batalla de los Bastardos."
        )
        
        tyrion_lannister = Character(
            name="Tyrion Lannister",
            title="Mano de la Reina",
            house_id=house_lannister._oid,
            status="Alive",
            description="El Gnomo, hermano menor de Cersei y Jaime, conocido por su inteligencia."
        )
        
        daenerys_targaryen = Character(
            name="Daenerys Targaryen",
            title="Madre de Dragones",
            house_id=house_targaryen._oid,
            status="Dead",
            description="La última Targaryen, conquistadora de Essos y pretendiente al Trono de Hierro."
        )
        
        arya_stark = Character(
            name="Arya Stark",
            title="Faceless Man",
            house_id=house_stark._oid,
            status="Alive",
            description="Hija menor de Ned Stark, entrenada como asesina sin rostro."
        )
        
        # Guardar personajes
        srp.save(jon_snow)
        srp.save(tyrion_lannister)
        srp.save(daenerys_targaryen)
        srp.save(arya_stark)
        
        # Crear eventos
        battle_bastards = Event(
            name="Batalla de los Bastardos",
            date="2016-06-19",
            location="Winterfell",
            description="Batalla épica entre Jon Snow y Ramsay Bolton por el control de Winterfell.",
            participants=[jon_snow._oid]
        )
        
        red_wedding = Event(
            name="La Boda Roja",
            date="2013-06-02",
            location="Los Gemelos",
            description="Masacre de los Stark durante la boda de Edmure Tully.",
            participants=[]
        )
        
        kings_landing_destruction = Event(
            name="Destrucción de Desembarco del Rey",
            date="2019-05-12",
            location="Desembarco del Rey",
            description="Daenerys destruye la capital con fuego de dragón.",
            participants=[daenerys_targaryen._oid]
        )
        
        # Guardar eventos
        srp.save(battle_bastards)
        srp.save(red_wedding)
        srp.save(kings_landing_destruction)
        
        print("Datos iniciales creados exitosamente!")
        
    except Exception as e:
        print(f"Error al inicializar datos de ejemplo: {e}")

if __name__ == "__main__":
    #initialize_sample_data()
    app.run(debug=True, host='0.0.0.0', port=8081)