import sirope
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user
from flask import session

class AuthController:
    def __init__(self, srp: sirope.Sirope):
        self.srp = srp

    def register_user(self, username, password, email):
        """Registra un nuevo usuario en el sistema"""
        # Verificar si el usuario ya existe
        if self.find_user_by_username(username) or self.find_user_by_email(email):
            return False, "El nombre de usuario o correo electrónico ya está en uso"
        
        # Crear nuevo usuario con contraseña hasheada
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username, hashed_password, email)
        
        # Guardar el usuario en sirope
        self.srp.save(new_user)
        return True, "Usuario registrado correctamente"

    def login_user_with_credentials(self, username, password):
        """Inicia sesión con nombre de usuario y contraseña"""
        user = self.find_user_by_username(username)
        if user and check_password_hash(user.password, password):
            # Hacer login con Flask-Login con remember=True para persistencia
            login_user(user, remember=True)
            
            # Guardar explícitamente en la sesión para asegurar que se actualice
            session.permanent = True  # Hacer la sesión permanente
            session['user_id'] = user.get_id()
            session['username'] = user.username
            session['is_authenticated'] = True
            session.modified = True
            
            return True, "Inicio de sesión exitoso"
        return False, "Nombre de usuario o contraseña incorrectos"

    def logout_current_user(self):
        """Cierra la sesión del usuario actual"""
        # Limpiar la sesión primero
        session.pop('user_id', None)
        session.pop('username', None)
        session.pop('is_authenticated', None)
        session.clear()  # Limpiar completamente la sesión
        session.modified = True
        
        # Luego cerrar sesión con Flask-Login
        logout_user()
        
        return True, "Sesión cerrada correctamente"

    def find_user_by_username(self, username):
        """Busca un usuario por su nombre de usuario"""
        query = lambda u: isinstance(u, User) and u.username == username
        users = list(self.srp.filter(User, query))
        return users[0] if users else None

    def find_user_by_email(self, email):
        """Busca un usuario por su correo electrónico"""
        query = lambda u: isinstance(u, User) and u.email == email
        users = list(self.srp.filter(User, query))
        return users[0] if users else None