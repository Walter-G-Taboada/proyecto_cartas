from flask import Blueprint, render_template, request, redirect, url_for, Response
from database.conection import get_db_connection
from routes.auth import login_requerido, requerir_roles
import datetime

precios_bp = Blueprint('precios', __name__)

@precios_bp.route('/listas_precios')
@login_requerido
@requerir_roles(1, 2, 3)  # Todos pueden verlo pero editarlo solo 1 y 2
def central_listas_precios():
    return redirect(url_for('locales.dashboard'))

@precios_bp.route('/local/<codigo_local>')
@login_requerido
@requerir_roles(1, 2, 3)  # Todos pueden verlo pero solo 1 y 2 pueden editar
def ver_precios_local(codigo_local):
    hoy = datetime.date.today()
    mes_actual = request.args.get('mes_vigencia', hoy.strftime('%m-%Y'))
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # 1. Traemos la info del local
    cursor.execute("SELECT id_local, nombre_local, codigo_local FROM locales WHERE codigo_local = %s", (codigo_local,))
    local_info = cursor.fetchone()
    if not local_info:
        cursor.close(); db.close(); return "Local no encontrado", 404
        
    # 2. Nueva Query Estratégica: Trae los productos, sus precios actuales para el mes 
    # Y con una subconsulta (MAX) busca el ÚLTIMO precio cargado en el historial para ese producto (sin importar el mes)
    query_productos = """
        SELECT p.id_producto, p.id_rubro, r.nombre_rubro, p.codigo_plato, p.nombre_plato, p.descripcion AS descripcion_plato,
               pl.id_precio AS id_precio_actual, pl.precio_efectivo AS precio_efectivo_actual, pl.precio_peya AS precio_peya_actual, 
               pl.porcentaje_diferencia AS porcentaje_incremento_actual, pl.activo,
               COALESCE(
                   (SELECT hp.precio_efectivo 
                    FROM historial_precios hp 
                    WHERE hp.id_local = pl.id_local AND hp.id_producto = pl.id_producto 
                    ORDER BY hp.id_historial DESC LIMIT 1), 
                   0.00
               ) AS precio_efectivo_anterior
        FROM precios_local pl
        INNER JOIN productos p ON pl.id_producto = p.id_producto
        LEFT JOIN rubros r ON p.id_rubro = r.id_rubro
        WHERE pl.id_local = %s AND pl.mes_vigencia = %s
        ORDER BY r.nombre_rubro ASC, p.nombre_plato ASC
    """
    cursor.execute(query_productos, (local_info['id_local'], mes_actual))
    lista_productos = cursor.fetchall()
    
    # 3. Lógica limpia para la pantalla: Si la columna azul está en 0, le copiamos el precio anterior encontrado
    for prod in lista_productos:
        precio_ant = float(prod['precio_efectivo_anterior'] or 0.00)
        precio_act = float(prod['precio_efectivo_actual'] or 0.00)
        
        if precio_act <= 0:
            prod['precio_efectivo_actual'] = precio_ant

    # Generamos la lista de meses para el selector visual del historial superior
    historial_meses = [hoy.strftime('%m-%Y')]
    for i in range(1, 6):
        mes_pasado = (hoy.replace(day=1) - datetime.timedelta(days=i*30)).strftime('%m-%Y')
        if mes_pasado not in historial_meses: historial_meses.append(mes_pasado)
            
    cursor.close(); db.close()
    return render_template('precios.html', local=local_info, productos=lista_productos, mes_actual=mes_actual, historial_meses=historial_meses)

@precios_bp.route('/guardar_precios_masivo', methods=['POST'])
@login_requerido
@requerir_roles(1, 2)  # 🔥 Solo deja pasar si session['rol'] == 1 y 2 (Admin) y Gerente
def guardar_precios_masivo():
    id_local_origen = request.form.get('id_local')
    mes_vigencia = request.form.get('mes_vigencia')
    codigo_local = request.form.get('codigo_local')
    
    db = get_db_connection()
    # Usamos dictionary=True para que consultar los datos de locales sea más cómodo y seguro
    cursor = db.cursor(dictionary=True)
    
    try:
        # 1. 🔥 CONSULTA ANALÍTICA: Averiguamos si el local pertenece a algún grupo
        cursor.execute("SELECT id_grupo FROM locales WHERE id_local = %s", (id_local_origen,))
        local_origen_info = cursor.fetchone()
        
        id_grupo_actual = local_origen_info['id_grupo'] if local_origen_info else None
        
        # Por defecto, la lista de locales afectados es solo el de origen
        locales_a_actualizar = [int(id_local_origen)]
        
        # Si el local pertenece a un grupo, traemos todas las sucursales activas de ese grupo
        if id_grupo_actual is not None:
            cursor.execute("SELECT id_local FROM locales WHERE id_grupo = %s AND activo = 1", (id_grupo_actual,))
            locales_del_grupo = cursor.fetchall()
            locales_a_actualizar = [int(l['id_local']) for l in locales_del_grupo]

        # Volvemos a un cursor tradicional para procesar las claves sin alterar tu código original
        cursor.close()
        cursor = db.cursor()

        # 2. Recorremos los campos que vienen del formulario Excel
        for clave in request.form.keys():
            if clave.startswith('precio_efectivo_'):
                id_precio = clave.replace('precio_efectivo_', '')
                
                precio_efectivo = request.form.get(f'precio_efectivo_{id_precio}') or 0.00
                porcentaje_diferencia = request.form.get(f'porcentaje_diferencia_{id_precio}') or 0.00
                precio_peya = request.form.get(f'precio_peya_{id_precio}') or 0.00
                activo = request.form.get(f'activo_{id_precio}') or 1
                
                # Obtenemos el id_producto real de esa fila de precios
                cursor.execute("SELECT id_producto FROM precios_local WHERE id_precio = %s", (id_precio,))
                resultado_prod = cursor.fetchone()
                
                if resultado_prod:
                    id_producto = resultado_prod[0]
                    
                    # 3. 🔥 ITERAMOS EN LOTE: Guardamos historial y actualizamos a todos los locales del grupo
                    for id_loc in locales_a_actualizar:
                        
                        # A. Guardamos el registro en el historial para cada local afectado
                        query_historial = """
                            INSERT INTO historial_precios 
                            (id_local, id_producto, precio_efectivo, precio_peya, porcentaje_diferencia, mes_vigencia) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(query_historial, (id_loc, id_producto, precio_efectivo, precio_peya, porcentaje_diferencia, mes_vigencia))
                    
                        # B. Actualizamos la tabla de precios vigentes por combinación de Local, Producto y Mes
                        query_update = """
                            UPDATE precios_local 
                            SET precio_efectivo = %s, porcentaje_diferencia = %s, precio_peya = %s, activo = %s 
                            WHERE id_local = %s AND id_producto = %s AND mes_vigencia = %s
                        """
                        cursor.execute(query_update, (precio_efectivo, porcentaje_diferencia, precio_peya, activo, id_loc, id_producto, mes_vigencia))
                        
        db.commit()
    except Exception as e:
        print(f"Error en guardado masivo en bloque con historial de grupo: {e}")
        db.rollback()
    finally:
        cursor.close()
        db.close()

    # El redirect ahora quedó correctamente tabulado y dentro del flujo de la función
    return redirect(url_for('precios.ver_precios_local', codigo_local=codigo_local))


@precios_bp.route('/local/<codigo_local>/exportar_excel')
@login_requerido
@requerir_roles(1, 2, 3)
def exportar_excel(codigo_local):
    mes_vigencia = request.args.get('mes_vigencia')
    
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # 1. Buscamos info del local
    cursor.execute("SELECT id_local, nombre_local FROM locales WHERE codigo_local = %s", (codigo_local,))
    local_info = cursor.fetchone()
    
    if not local_info:
        cursor.close(); db.close(); return "Local no encontrado", 404
        
    # 2. Traemos la lista de precios actual de la base de datos
    query = """
        SELECT r.nombre_rubro, p.codigo_plato, p.nombre_plato, 
               pl.precio_efectivo, pl.precio_peya, pl.porcentaje_diferencia
        FROM precios_local pl
        INNER JOIN productos p ON pl.id_producto = p.id_producto
        LEFT JOIN rubros r ON p.id_rubro = r.id_rubro
        WHERE pl.id_local = %s AND pl.mes_vigencia = %s
        ORDER BY r.nombre_rubro ASC, p.nombre_plato ASC
    """
    cursor.execute(query, (local_info['id_local'], mes_vigencia))
    productos = cursor.fetchall()
    
    cursor.close(); db.close()
    
    # 3. Construimos el contenido del archivo Excel (Formato CSV compatible con Excel)
    # Metemos el BOM de UTF-8 para que Excel reconozca eñes y acentos de una
    contenido_csv = "\xef\xbb\xbf" 
    contenido_csv += f"Lista de Precios - Local: {local_info['nombre_local']} - Mes: {mes_vigencia}\n\n"
    contenido_csv += "Rubro;Codigo;Producto;Precio Efectivo;Precio Peya;% Incremento\n"
    
    for prod in productos:
        nombre_rubro = prod['nombre_rubro'] or 'Sin Rubro'
        codigo_plato = prod['codigo_plato'] or ''
        nombre_plato = prod['nombre_plato'] or ''
        precio_ef = str(prod['precio_efectivo'] or 0.00).replace('.', ',')
        precio_py = str(prod['precio_peya'] or 0.00).replace('.', ',')
        porcentaje = str(prod['porcentaje_diferencia'] or 0.00).replace('.', ',')
        
        contenido_csv += f'"{nombre_rubro}";"{codigo_plato}";"{nombre_plato}";{precio_ef};{precio_py};{porcentaje}\n'
    
    # 4. Escupimos la respuesta directo para descarga de navegador
    nombre_archivo = f"precios_{codigo_local}_{mes_vigencia}.csv"
    return Response(
        contenido_csv,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={nombre_archivo}"}
    )