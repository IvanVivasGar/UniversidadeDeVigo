from flask import Flask
from flask_login import LoginManager
from config import Config
import redis
import sys
import os

# Agregar el directorio sirope-master al path
sirope_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sirope-master')
sys.path.insert(0, sirope_path)
import sirope

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Debes iniciar sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Configurar Redis y Sirope
    try:
        redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB'],
            decode_responses=False
        )
        # Inicializar sirope correctamente
        app.sirope = sirope.Sirope(redis_client)
    except Exception as e:
        print(f"Error conectando con Redis: {e}")
        app.sirope = None
    
    # Registrar blueprints
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.routes.characters import bp as characters_bp
    app.register_blueprint(characters_bp, url_prefix='/characters')
    
    from app.routes.houses import bp as houses_bp
    app.register_blueprint(houses_bp, url_prefix='/houses')
    
    from app.routes.events import bp as events_bp
    app.register_blueprint(events_bp, url_prefix='/events')
    
    from app.routes.posts import bp as posts_bp
    app.register_blueprint(posts_bp, url_prefix='/posts')
    
    from app.routes.discussions import bp as discussions_bp
    app.register_blueprint(discussions_bp, url_prefix='/discussions')
    
    # Register admin routes
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)
    
    # Register API routes at root level
    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    try:
        from flask import current_app
        if current_app.sirope:
            return current_app.sirope.load(sirope.OID.from_text(user_id))
        return None
    except Exception as e:
        print(f"Error loading user: {e}")
        return None