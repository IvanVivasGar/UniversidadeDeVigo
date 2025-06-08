from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
import sirope
from controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)
srp = sirope.Sirope()
auth_controller = AuthController(srp)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        
        if not username or not password or not email:
            flash('Todos los campos son obligatorios', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('auth/register.html')
            
        success, message = auth_controller.register_user(username, password, email)
        if success:
            flash(message, 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(message, 'danger')
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Por favor, introduce tu nombre de usuario y contraseña', 'danger')
            return render_template('auth/login.html')
            
        success, message = auth_controller.login_user_with_credentials(username, password)
        if success:
            flash(message, 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash(message, 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    # No necesitamos @login_required aquí para que no redireccione al login
    from flask import session
    
    # Limpiar la sesión explícitamente
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('is_authenticated', None)
    session.clear()  # Limpiar por completo
    session.modified = True
    
    # Llamar al controlador para cerrar sesión con Flask-Login
    success, message = auth_controller.logout_current_user()
    flash(message, 'success')
    
    # Redirigir a la página de inicio
    return redirect(url_for('index'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html')