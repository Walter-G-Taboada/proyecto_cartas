# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, abort
from database.conection import get_db_connection
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# --- DECORADOR 1: VALIDAR LOGUEO ---
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Corregido: Si no existe 'user' en la sesión, al login directo
        if 'user' not in session:
            return redirect(url_for('auth.index')) 
        return f(*args, **kwargs)
    return decorated_function


# --- DECORADOR 2: VALIDAR ROLES (NUEVO) ---
def requerir_roles(*roles_permitidos):
    """
    Uso: @requerir_roles(1, 2) -> Permite solo a los ID de rol pasados por parámetro.
    """
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            # 1. Primero nos aseguramos de que esté logueado
            if 'user' not in session:
                return redirect(url_for('auth.index'))
            
            # 2. Tu sesión guarda el ID numérico en session['rol'] (1, 2, 3...)
            usuario_rol = session.get('rol')
            
            # 3. Si su rol no está autorizado, le tiramos un 403 (Prohibido)
            if usuario_rol not in roles_permitidos:
                abort(403)
                
            return f(*args, **kwargs)
        return funcion_decorada
    return decorador


@auth_bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('locales.dashboard')) 
    return render_template('login.html')


@auth_bp.route('/login', methods=['POST'])
def login():
    user_input = request.form.get('username')
    pass_input = request.form.get('password')
    
    db = get_db_connection()
    if db is None: 
        return "Error de conexión", 500
        
    cursor = db.cursor(dictionary=True)
    query = "SELECT username, password, id_role, activo FROM usuarios WHERE username = %s"
    cursor.execute(query, (user_input,))
    usuario_db = cursor.fetchone()
    
    cursor.close()
    db.close()

    if usuario_db and usuario_db['password'] == pass_input:
        if usuario_db['activo'] == 1:
            # Seteo de sesión impecable con tus variables reales
            session['user'] = usuario_db['username']
            session['rol'] = usuario_db['id_role'] # 👈 Guarda 1, 2 o 3
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