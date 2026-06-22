from flask import Blueprint, render_template, request, redirect, url_for
from database.conection import get_db_connection
from routes.auth import login_requerido, requerir_roles
import datetime

productos_bp = Blueprint('productos', __name__)

# --- RUBROS ---
@productos_bp.route('/rubros')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def rubros():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_rubro, nombre_rubro, activo FROM rubros ORDER BY id_rubro DESC")
    lista_rubros = cursor.fetchall()
    cursor.close(); db.close()
    return render_template('rubros.html', rubros=lista_rubros)

@productos_bp.route('/guardar_rubro', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def guardar_rubro():
    nombre = request.form.get('nombre_rubro')
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO rubros (nombre_rubro, activo) VALUES (%s, 1)", (nombre,))
        db.commit()
    except Exception as e:
        print(f"Error: {e}"); db.rollback()
    finally:
        cursor.close(); db.close()
    return redirect(url_for('productos.rubros'))

@productos_bp.route('/editar_rubro/<int:id_rubro>')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def editar_rubro(id_rubro):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id_rubro, nombre_rubro FROM rubros WHERE id_rubro = %s", (id_rubro,))
    rubro_a_editar = cursor.fetchone()
    cursor.close(); db.close()
    return render_template('editar_rubro.html', rubro=rubro_a_editar)

@productos_bp.route('/actualizar_rubro', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def actualizar_rubro():
    id_rubro = request.form.get('id_rubro')
    nombre = request.form.get('nombre_rubro')
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE rubros SET nombre_rubro = %s WHERE id_rubro = %s", (nombre, id_rubro))
        db.commit()
    except Exception as e:
        print(f"Error: {e}"); db.rollback()
    finally:
        cursor.close(); db.close()
    return redirect(url_for('productos.rubros'))

@productos_bp.route('/cambiar_estado_rubro/<int:id_rubro>')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def cambiar_estado_rubro(id_rubro):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT activo FROM rubros WHERE id_rubro = %s", (id_rubro,))
    rubro = cursor.fetchone()
    if rubro:
        nuevo_estado = 0 if rubro['activo'] == 1 else 1
        cursor.execute("UPDATE rubros SET activo = %s WHERE id_rubro = %s", (nuevo_estado, id_rubro))
        db.commit()
    cursor.close(); db.close()
    return redirect(url_for('productos.rubros'))

# --- PLATOS / PRODUCTOS ---
@productos_bp.route('/productos')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def productos():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id_producto, p.codigo_plato, p.nombre_plato, r.nombre_rubro, c.nombre_categoria 
        FROM productos p 
        LEFT JOIN rubros r ON p.id_rubro = r.id_rubro 
        LEFT JOIN categorias c ON p.id_categoria = c.id_categoria
        ORDER BY p.id_producto DESC
    """)
    lista_productos = cursor.fetchall()
    
    cursor.execute("SELECT id_rubro, nombre_rubro FROM rubros WHERE activo = 1 ORDER BY nombre_rubro ASC")
    lista_rubros = cursor.fetchall()
    cursor.execute("SELECT id_local, nombre_local FROM locales WHERE activo = 1 ORDER BY nombre_local ASC")
    lista_locales = cursor.fetchall()
    cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria ASC")
    lista_categorias = cursor.fetchall()
    
    cursor.close(); db.close()
    return render_template('plato.html', productos=lista_productos, rubros=lista_rubros, locales=lista_locales, categorias=lista_categorias)

@productos_bp.route('/guardar_producto', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)
def guardar_producto():
    # 1. Captura de datos del formulario
    id_rubro = request.form.get('id_rubro')
    id_categoria = request.form.get('id_categoria')
    codigo_plato = request.form.get('codigo').upper()
    nombre_plato = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    condicion = request.form.get('condicion')
    locales_seleccionados = [int(x) for x in request.form.getlist('locales_seleccionados')]
    mes_actual = datetime.datetime.now().strftime("%m-%Y")
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
        # 2. Sentencia SQL corregida (6 campos = 6 %s)
        # Asegúrate que el orden aquí coincida con la tupla de datos abajo
        query = """INSERT INTO productos 
                   (id_rubro, id_categoria, codigo_plato, nombre_plato, descripcion, condicion) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        
        datos = (id_rubro, id_categoria, codigo_plato, nombre_plato, descripcion, condicion)
        
        cursor.execute(query, datos)
        
        id_nuevo_producto = cursor.lastrowid
        
        # 3. Guardado de precios locales
        for id_local in locales_seleccionados:
            cursor.execute("""INSERT INTO precios_local 
                              (id_local, id_producto, precio_efectivo, precio_peya, porcentaje_diferencia, mes_vigencia, activo) 
                              VALUES (%s, %s, 0.00, 0.00, 0.00, %s, 1)""", 
                           (id_local, id_nuevo_producto, mes_actual))
        db.commit()
        print("¡Producto guardado exitosamente!")
    except Exception as e:
        print(f"Error al guardar: {e}")
        db.rollback()
    finally:
        cursor.close(); db.close()
    return redirect(url_for('productos.productos'))

@productos_bp.route('/editar_producto/<int:id>')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def editar_producto(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT p.*, r.nombre_rubro, c.nombre_categoria FROM productos p LEFT JOIN rubros r ON p.id_rubro = r.id_rubro LEFT JOIN categorias c ON p.id_categoria = c.id_categoria ORDER BY r.nombre_rubro ASC, p.nombre_plato ASC")
        productos_lista = cursor.fetchall()
        cursor.execute("SELECT * FROM rubros WHERE activo = 1 ORDER BY nombre_rubro ASC")
        rubros_lista = cursor.fetchall()
        cursor.execute("SELECT id_local, nombre_local, codigo_local FROM locales WHERE activo = 1 ORDER BY nombre_local ASC")
        locales_lista = cursor.fetchall()
        cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria ASC")
        categorias_lista = cursor.fetchall()
        
        cursor.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
        producto_edicion = cursor.fetchone()

        if producto_edicion:
            mes_actual = datetime.datetime.now().strftime("%m-%Y")
            cursor.execute("SELECT id_local FROM precios_local WHERE id_producto = %s AND mes_vigencia = %s", (id, mes_actual))
            producto_edicion['locales_asociados'] = [row['id_local'] for row in cursor.fetchall()]
    finally:
        cursor.close(); db.close()
    return render_template('plato.html', productos=productos_lista, rubros=rubros_lista, locales=locales_lista, categorias=categorias_lista, producto_edicion=producto_edicion)

@productos_bp.route('/actualizar_producto', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def actualizar_producto():
    id_producto = request.form.get('id_producto')
    id_rubro = request.form.get('id_rubro')
    id_categoria = request.form.get('id_categoria')
    codigo_plato = request.form.get('codigo').upper()
    nombre_plato = request.form.get('nombre')
    condicion = request.form.get('condicion')
    descripcion = request.form.get('descripcion')
    locales_seleccionados = [int(x) for x in request.form.getlist('locales_seleccionados')]
    mes_actual = datetime.datetime.now().strftime("%m-%Y")
    
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE productos SET id_rubro = %s, id_categoria = %s, codigo_plato = %s, nombre_plato =%s, condicion = %s, descripcion = %s, WHERE id_producto = %s", (id_rubro, id_categoria, codigo_plato, nombre_plato, id_producto))
        cursor.execute("SELECT id_local FROM precios_local WHERE id_producto = %s AND mes_vigencia = %s", (id_producto, mes_actual))
        locales_actuales_db = [row[0] for row in cursor.fetchall()]
        
        for id_local_db in locales_actuales_db:
            if id_local_db not in locales_seleccionados:
                cursor.execute("DELETE FROM precios_local WHERE id_producto = %s AND id_local = %s AND mes_vigencia = %s", (id_producto, id_local_db, mes_actual))
        for id_local_nuevo in locales_seleccionados:
            if id_local_nuevo not in locales_actuales_db:
                cursor.execute("INSERT INTO precios_local (id_local, id_producto, precio_efectivo, precio_peya, porcentaje_diferencia, mes_vigencia, activo) VALUES (%s, %s, 0.00, 0.00, 0.00, %s, 1)", (id_local_nuevo, id_producto, mes_actual))
        db.commit()
    except Exception as e:
        print(f"Error: {e}"); db.rollback()
    finally:
        cursor.close(); db.close()
    return redirect(url_for('productos.productos'))

@productos_bp.route('/borrar_producto/<int:id_producto>')
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def borrar_producto(id_producto):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        db.commit()
    except Exception as e:
        print(f"Error: {e}"); db.rollback()
    finally:
        cursor.close(); db.close()
    return redirect(url_for('productos.productos'))