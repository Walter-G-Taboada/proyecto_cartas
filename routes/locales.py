from flask import Blueprint, render_template, request, redirect, url_for
from database.conection import get_db_connection
from routes.auth import login_requerido, requerir_roles  # Importamos el decorador de seguridad

locales_bp = Blueprint('locales', __name__)

@locales_bp.route('/dashboard')
@login_requerido
@requerir_roles(1, 2, 3)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def dashboard():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_local, nombre_local, codigo_local FROM locales WHERE activo = 1 ORDER BY nombre_local ASC")
    lista_locales = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('dashboard.html', locales=lista_locales)

@locales_bp.route('/locales')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def locales():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_local, nombre_local, codigo_local, activo FROM locales ORDER BY id_local DESC")
    lista_locales = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('locales.html', locales=lista_locales)

@locales_bp.route('/guardar_local', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def guardar_local():
    codigo = request.form.get('codigo').upper()
    nombre = request.form.get('nombre')
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO locales (codigo_local, nombre_local, activo) VALUES (%s, %s, 1)", (codigo, nombre))
        db.commit()
    except Exception as e:
        print(f"Error: {e}"); db.rollback()
    finally:
        cursor.close(); db.close()
    return redirect(url_for('locales.locales'))

@locales_bp.route('/editar_local/<int:id_local>')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def editar_local(id_local):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_local, nombre_local, codigo_local FROM locales WHERE id_local = %s", (id_local,))
    local_a_editar = cursor.fetchone()
    cursor.close(); db.close()
    return render_template('editar_local.html', local=local_a_editar)

@locales_bp.route('/actualizar_local', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def actualizar_local():
    id_local = request.form.get('id_local')
    codigo = request.form.get('codigo').upper()
    nombre = request.form.get('nombre')
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE locales SET codigo_local = %s, nombre_local = %s WHERE id_local = %s", (codigo, nombre, id_local))
        db.commit()
    except Exception as e:
        print(f"Error: {e}"); db.rollback()
    finally:
        cursor.close(); db.close()
    return redirect(url_for('locales.locales'))

@locales_bp.route('/cambiar_estado_local/<int:id_local>')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def cambiar_estado_local(id_local):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT activo FROM locales WHERE id_local = %s", (id_local,))
    local = cursor.fetchone()
    if local:
        nuevo_estado = 0 if local['activo'] == 1 else 1
        cursor.execute("UPDATE locales SET activo = %s WHERE id_local = %s", (nuevo_estado, id_local))
        db.commit()
    cursor.close(); db.close()
    return redirect(url_for('locales.locales'))