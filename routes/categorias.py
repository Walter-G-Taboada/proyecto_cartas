# routes/categorias.py
from flask import Blueprint, render_template, request, redirect, url_for
from database.conection import get_db_connection  # Traemos tu función de conexión
from routes.auth import login_requerido          # Tu decorador de seguridad

categorias_bp = Blueprint('categorias', __name__)

# --- RUTA: LISTAR Y CREAR CATEGORÍAS ---
@categorias_bp.route('/dashboard/categorias', methods=['GET', 'POST'])
@login_requerido
def dashboard_categorias():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True) # dictionary=True para poder usar cat.id_categoria en el HTML
    
    if request.method == 'POST':
        nombre = request.form.get('nombre_categoria').strip()
        
        if nombre:
            try:
                # Usamos un cursor limpio para la inserción
                cursor_insert = db.cursor()
                cursor_insert.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
                db.commit()
                cursor_insert.close()
            except Exception as e:
                print(f"Error o duplicado al insertar categoría: {e}")
                db.rollback()
                
            # Cerramos todo antes de redireccionar
            cursor.close()
            db.close()
            return redirect(url_for('categorias.dashboard_categorias'))
            
    # Si es GET, listamos todas las categorías
    cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias ORDER BY nombre_categoria ASC")
    lista_categorias = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('categorias.html', categorias=lista_categorias)


# --- RUTA: EDITAR CATEGORÍA ---
@categorias_bp.route('/dashboard/categorias/editar/<int:id_cat>', methods=['GET', 'POST'])
@login_requerido
def editar_categoria(id_cat):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # SI EL USUARIO HACE CLIC EN GUARDAR (POST)
    if request.method == 'POST':
        nombre = request.form.get('nombre_categoria')
        if nombre:
            nombre = nombre.strip()
            try:
                cursor.execute("UPDATE categorias SET nombre_categoria = %s WHERE id_categoria = %s", (nombre, id_cat))
                db.commit()
            except Exception as e:
                print(f"Error al editar categoría: {e}")
                db.rollback()
            finally:
                cursor.close()
                db.close()
        return redirect(url_for('categorias.dashboard_categorias'))

    # SI EL USUARIO SOLO HACE CLIC EN EL BOTÓN PARA ENTRAR A EDITAR (GET)
    cursor.execute("SELECT id_categoria, nombre_categoria FROM categorias WHERE id_categoria = %s", (id_cat,))
    categoria_a_editar = cursor.fetchone()
    
    cursor.close()
    db.close()
    
    if not categoria_a_editar:
        return "Categoría no encontrada", 404
        
    return render_template('editar_categoria.html', categoria=categoria_a_editar)

# --- RUTA: ELIMINAR CATEGORÍA ---
@categorias_bp.route('/dashboard/categorias/eliminar/<int:id_cat>', methods=['POST'])
@login_requerido
def eliminar_categoria(id_cat):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM categorias WHERE id_categoria = %s", (id_cat,))
        db.commit()
    except Exception as e:
        print(f"No se pudo eliminar la categoría (posiblemente en uso): {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('categorias.dashboard_categorias'))