from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.utils.helpers import get_entity_by_name
import sys
import os

# Agregar sirope al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sirope-master'))
import sirope

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        try:
            user = get_entity_by_name(current_app.sirope, User, username)
            
            if user and user.check_password(password):
                login_user(user)
                return jsonify({'success': True, 'message': f'¡Bienvenido, {user.username}!'})
            else:
                return jsonify({'success': False, 'message': 'Usuario o contraseña incorrectos'})
                
        except Exception as e:
            print(f"Error en login: {e}")
            return jsonify({'success': False, 'message': 'Error en el servidor'})
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Página de registro"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        terms = request.form.get('terms')
        
        # Validaciones básicas
        if not username or not email or not password or not confirm_password:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        if password != confirm_password:
            return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'La contraseña debe tener al menos 6 caracteres'})
        
        if not terms:
            return jsonify({'success': False, 'message': 'Debes aceptar los términos y condiciones'})
        
        # Validar formato de email
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return jsonify({'success': False, 'message': 'Formato de email inválido'})
        
        # Validar username
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': 'El nombre de usuario debe tener entre 3 y 20 caracteres'})
        
        username_regex = r'^[a-zA-Z0-9_]+$'
        if not re.match(username_regex, username):
            return jsonify({'success': False, 'message': 'El nombre de usuario solo puede contener letras, números y guiones bajos'})
        
        try:
            # Verificar si el usuario ya existe
            existing_user = get_entity_by_name(current_app.sirope, User, username)
            if existing_user:
                return jsonify({'success': False, 'message': 'El nombre de usuario ya existe'})
            
            # Verificar email único
            existing_email = current_app.sirope.find_first(User, lambda u: u.email.lower() == email.lower())
            if existing_email:
                return jsonify({'success': False, 'message': 'El email ya está registrado'})
            
            # Crear nuevo usuario
            user = User(username, email)
            user.set_password(password)
            current_app.sirope.save(user)
            
            # Iniciar sesión automáticamente
            login_user(user)
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True, 
                    'message': f'¡Registro exitoso! Bienvenido, {user.username}!',
                    'redirect_url': url_for('main.index')
                })
            else:
                flash(f'¡Registro exitoso! Bienvenido, {user.username}!', 'success')
                return redirect(url_for('main.index'))
            
        except Exception as e:
            print(f"Error en registro: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': 'Error en el servidor. Por favor, inténtalo de nuevo.'})
    
    return render_template('auth/register.html')

@bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    """Página de perfil del usuario"""
    try:
        # Obtener posts del usuario
        user_posts = []
        for post_oid in current_user.posts:
            try:
                post = current_app.sirope.load(post_oid)
                if post:
                    user_posts.append(post)
            except:
                continue
        
        # Ordenar posts por fecha
        user_posts.sort(key=lambda p: p.created_at, reverse=True)
        
        # Obtener discusiones iniciadas por el usuario
        from app.models.discussion import Discussion
        user_discussions = []
        try:
            all_discussions = list(current_app.sirope.load_all(Discussion))
            user_discussions = [d for d in all_discussions if d.author_oid == current_user.__oid__]
            # Ordenar discusiones por fecha
            user_discussions.sort(key=lambda d: d.created_at, reverse=True)
        except Exception as e:
            print(f"Error cargando discusiones del usuario: {e}")
        
        return render_template('profile/profile.html', 
                             user=current_user, 
                             user_posts=user_posts,
                             user_discussions=user_discussions)
        
    except Exception as e:
        print(f"Error en perfil: {e}")
        return render_template('profile/profile.html', 
                             user=current_user, 
                             user_posts=[],
                             user_discussions=[])

@bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    """Actualizar información del perfil del usuario"""
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        
        # Validaciones básicas
        if not username or not email:
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'})
        
        # Validar formato de email
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return jsonify({'success': False, 'message': 'Formato de email inválido'})
        
        # Validar username
        if len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': 'El nombre de usuario debe tener entre 3 y 20 caracteres'})
        
        username_regex = r'^[a-zA-Z0-9_]+$'
        if not re.match(username_regex, username):
            return jsonify({'success': False, 'message': 'El nombre de usuario solo puede contener letras, números y guiones bajos'})
        
        # Verificar si el username ya existe (excepto el actual)
        if username != current_user.username:
            existing_user = get_entity_by_name(current_app.sirope, User, username)
            if existing_user:
                return jsonify({'success': False, 'message': 'El nombre de usuario ya existe'})
        
        # Verificar email único (excepto el actual)
        if email.lower() != current_user.email.lower():
            existing_email = current_app.sirope.find_first(User, lambda u: u.email.lower() == email.lower())
            if existing_email:
                return jsonify({'success': False, 'message': 'El email ya está registrado'})
        
        # Actualizar datos del usuario
        current_user.username = username
        current_user.email = email
        
        # Manejar avatar si se subió uno
        if 'avatar' in request.files:
            avatar_file = request.files['avatar']
            if avatar_file and avatar_file.filename:
                # Aquí se podría implementar la subida de archivos
                # Por ahora solo guardamos un placeholder
                pass
        
        # Guardar cambios
        current_app.sirope.save(current_user)
        
        return jsonify({
            'success': True, 
            'message': '¡Perfil actualizado exitosamente!'
        })
        
    except Exception as e:
        print(f"Error al actualizar perfil: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor. Por favor, inténtalo de nuevo.'})