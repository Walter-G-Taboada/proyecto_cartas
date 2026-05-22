# routes/usuarios.py
from flask import Blueprint, render_template, request, redirect, url_for
from database.conection import get_db_connection
from routes.auth import login_requerido, requerir_roles

usuarios_bp = Blueprint('usuarios', __name__)

# --- RUTA: LISTAR Y CREAR USUARIOS ---
@usuarios_bp.route('/dashboard/usuarios', methods=['GET', 'POST'])
@login_requerido
@requerir_roles(1)  # 🔥 Solo deja pasar si session['rol'] == 1 (Admin)
def dashboard_usuarios():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        id_role = request.form.get('id_role')
        
        if username and password and id_role:
            try:
                cursor_insert = db.cursor()
                cursor_insert.execute(
                    "INSERT INTO usuarios (username, password, id_role, activo) VALUES (%s, %s, %s, 1)", 
                    (username, password, int(id_role))
                )
                db.commit()
                cursor_insert.close()
            except Exception as e:
                print(f"Error o duplicado al insertar usuario: {e}")
                db.rollback()
                
            cursor.close()
            db.close()
            return redirect(url_for('usuarios.dashboard_usuarios'))
            
    # 1. Traemos los usuarios haciendo un INNER JOIN con la tabla roles para traer el nombre real
    cursor.execute("""
        SELECT u.id_usuario, u.username, u.id_role, u.activo, r.nombre_role 
        FROM usuarios u
        INNER JOIN roles r ON u.id_role = r.id_role
        ORDER BY u.username ASC
    """)
    lista_usuarios = cursor.fetchall()
    
    # 2. Traemos TODOS los roles disponibles para llenar el select del formulario dinámicamente
    cursor.execute("SELECT id_role, nombre_role FROM roles ORDER BY id_role ASC")
    lista_roles = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('usuarios.html', usuarios=lista_usuarios, roles=lista_roles)


# --- RUTA: EDITAR USUARIO (Vista Separada) ---
@usuarios_bp.route('/dashboard/usuarios/editar/<int:id_user>', methods=['GET', 'POST'])
@login_requerido
@requerir_roles(1)  # 🔥 Solo deja pasar si session['rol'] == 1 (Admin)
def editar_usuario(id_user):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form.get('username')
        id_role = request.form.get('id_role')
        password = request.form.get('password')
        activo = request.form.get('activo')
        
        status_activo = 1 if activo else 0
        
        if username and id_role:
            username = username.strip()
            try:
                if password and password.strip():
                    password = password.strip()
                    cursor.execute(
                        "UPDATE usuarios SET username = %s, password = %s, id_role = %s, activo = %s WHERE id_usuario = %s", 
                        (username, password, int(id_role), status_activo, id_user)
                    )
                else:
                    cursor.execute(
                        "UPDATE usuarios SET username = %s, id_role = %s, activo = %s WHERE id_usuario = %s", 
                        (username, int(id_role), status_activo, id_user)
                    )
                db.commit()
            except Exception as e:
                print(f"Error al editar usuario: {e}")
                db.rollback()
            finally:
                cursor.close()
                db.close()
        return redirect(url_for('usuarios.dashboard_usuarios'))

    # Método GET: Buscamos el usuario actual
    cursor.execute("SELECT id_usuario, username, id_role, activo FROM usuarios WHERE id_usuario = %s", (id_user,))
    usuario_a_editar = cursor.fetchone()
    
    # También traemos los roles para el select de la pantalla de edición
    cursor.execute("SELECT id_role, nombre_role FROM roles ORDER BY id_role ASC")
    lista_roles = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    if not usuario_a_editar:
        return "Usuario no encontrado", 404
        
    return render_template('editar_usuario.html', usuario=usuario_a_editar, roles=lista_roles)


# --- RUTA: ELIMINAR USUARIO ---
@usuarios_bp.route('/dashboard/usuarios/eliminar/<int:id_user>', methods=['POST'])
@login_requerido
@requerir_roles(1)  # 🔥 Solo deja pasar si session['rol'] == 1 (Admin)
def eliminar_usuario(id_user):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_user,))
        db.commit()
    except Exception as e:
        print(f"No se pudo eliminar el usuario: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('usuarios.dashboard_usuarios'))