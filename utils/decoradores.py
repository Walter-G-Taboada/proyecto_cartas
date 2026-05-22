# utils/decoradores.py
from functools import wraps
from flask import session, abort, redirect, url_for, flash

def requerir_roles(*roles_permitidos):
    """
    Decorador para restringir el acceso a rutas según el id_role del usuario.
    Ejemplo de uso: @requerir_roles(1, 2)  -> Solo Admin (1) y Gerente (2)
    """
    def decorador(f):
        @wraps(f)
        def funcion_decorada(*args, **kwargs):
            # 1. Validar que esté logueado
            if 'id_usuario' not in session:
                return redirect(url_for('auth.login'))
            
            # 2. Validar si su id_role está dentro de los permitidos
            # Nota: Asegurate de guardar 'id_role' en la sesión cuando el usuario hace el Login
            usuario_rol = session.get('id_role')
            
            if usuario_rol not in roles_permitidos:
                # Si no tiene permiso, lo rebotamos con un error 403 (Prohibido)
                # O podés redirigirlo al dashboard con un mensaje de alerta
                abort(403) 
                
            return f(*args, **kwargs)
        return funcion_decorada
    return decorador