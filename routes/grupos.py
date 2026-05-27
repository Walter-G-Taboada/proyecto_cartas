# routes/grupos.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.conection import get_db_connection
from routes.auth import login_requerido, requerir_roles

grupos_bp = Blueprint('grupos', __name__)

# 📋 LISTADO PRINCIPAL (ABM)
@grupos_bp.route('/grupos')
@login_requerido
@requerir_roles(1, 2, 3) # Todos pueden ver los grupos creados
def listar_grupos():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # 🔥 REVISADO: Se agregó GROUP_CONCAT para empaquetar los IDs asociados (Ej: "1,4,7")
    query_grupos = """
        SELECT g.*, COUNT(l.id_local) AS cantidad_locales,
               GROUP_CONCAT(l.id_local) AS ids_locales_asociados
        FROM grupos_locales g
        LEFT JOIN locales l ON g.id_grupo = l.id_grupo
        GROUP BY g.id_grupo
        ORDER BY g.nombre_grupo ASC
    """
    cursor.execute(query_grupos)
    grupos = cursor.fetchall()
    
    # 2. Traemos los locales activos para armar el panel de checkboxes (Alta y Edición)
    cursor.execute("SELECT id_local, nombre_local, codigo_local FROM locales WHERE activo = 1 ORDER BY nombre_local ASC")
    locales_disponibles = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('grupos.html', grupos=grupos, locales_disponibles=locales_disponibles)


# 📥 PROCESAR ALTA DE GRUPO CON ASIGNACIÓN EN LOTE
@grupos_bp.route('/grupos/guardar', methods=['POST'])
@login_requerido
@requerir_roles(1, 2) # Solo Admin y Costos/Gerente crean grupos
def guardar_grupo():
    nombre = request.form.get('nombre_grupo')
    descripcion = request.form.get('descripcion')
    locales_seleccionados = request.form.getlist('locales_seleccionados')
    
    if not nombre:
        return redirect(url_for('grupos.listar_grupos'))
        
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Step 1: Insertamos el nuevo grupo de locales
        cursor.execute(
            "INSERT INTO grupos_locales (nombre_grupo, descripcion) VALUES (%s, %s)",
            (nombre, descripcion)
        )
        nuevo_id_grupo = cursor.lastrowid
        
        # Step 2: Vinculamos los locales seleccionados en lote
        if locales_seleccionados:
            format_strings = ', '.join(['%s'] * len(locales_seleccionados))
            query_update_locales = f"""
                UPDATE locales 
                SET id_grupo = %s 
                WHERE id_local IN ({format_strings})
            """
            parametros = [nuevo_id_grupo] + [int(id_loc) for id_loc in locales_seleccionados]
            cursor.execute(query_update_locales, parametros)
            
        db.commit()
        
    except Exception as e:
        print(f"Error crítico al crear grupo y asignar locales: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('grupos.listar_grupos'))

    
# 🔄 PROCESAR EDICIÓN/ACTUALIZACIÓN DE GRUPO
@grupos_bp.route('/grupos/actualizar', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)  # Solo perfiles con permisos de edición
def actualizar_grupo():
    id_grupo = request.form.get('id_grupo')
    nombre = request.form.get('nombre_grupo')
    descripcion = request.form.get('descripcion')
    locales_seleccionados = request.form.getlist('locales_seleccionados')
    
    if not id_grupo or not nombre:
        return redirect(url_for('grupos.listar_grupos'))
        
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # 1. Actualizamos los datos básicos del grupo
        cursor.execute(
            "UPDATE grupos_locales SET nombre_grupo = %s, descripcion = %s WHERE id_grupo = %s",
            (nombre, descripcion, id_grupo)
        )
        
        # 2. Rompemos la relación vieja (limpieza preventiva)
        cursor.execute("UPDATE locales SET id_grupo = NULL WHERE id_grupo = %s", (id_grupo,))
        
        # 3. Construimos la relación nueva en lote si vinieron tildados
        if locales_seleccionados:
            format_strings = ', '.join(['%s'] * len(locales_seleccionados))
            query_update_locales = f"""
                UPDATE locales 
                SET id_grupo = %s 
                WHERE id_local IN ({format_strings})
            """
            parametros = [id_grupo] + [int(id_loc) for id_loc in locales_seleccionados]
            cursor.execute(query_update_locales, parametros)
            
        db.commit()
        
    except Exception as e:
        print(f"Error crítico al actualizar grupo: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()
        
    return redirect(url_for('grupos.listar_grupos'))