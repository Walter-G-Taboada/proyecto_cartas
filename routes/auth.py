from flask import Blueprint, render_template, request, redirect, url_for, session
from database.conection import get_db_connection
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Exportamos el decorador para usarlo en los demás blueprints
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.index')) # Apesta al index de este blueprint
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('locales.dashboard')) # Apunta al dashboard que estará en locales
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    user_input = request.form.get('username')
    pass_input = request.form.get('password')
    
    db = get_db_connection()
    if db is None: return "Error de conexión", 500
        
    cursor = db.cursor(dictionary=True)
    query = "SELECT username, password, id_role, activo FROM usuarios WHERE username = %s"
    cursor.execute(query, (user_input,))
    usuario_db = cursor.fetchone()
    
    cursor.close()
    db.close()

    if usuario_db and usuario_db['password'] == pass_input:
        if usuario_db['activo'] == 1:
            session['user'] = usuario_db['username']
            session['rol'] = usuario_db['id_role']
            session['nombre_real'] = usuario_db['username'].capitalize()
            return redirect(url_for('locales.dashboard'))
        else:
            return "Tu usuario está deshabilitado", 403
    else:
        return "Usuario o contraseña incorrectos", 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))