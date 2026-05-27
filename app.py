from flask import Flask, render_template
from routes.auth import auth_bp
from routes.locales import locales_bp
from routes.productos import productos_bp
from routes.precios import precios_bp
from routes.categorias import categorias_bp
from routes.usuarios import usuarios_bp
from routes.grupos import grupos_bp

app = Flask(__name__)
app.secret_key = 'baum_secret_key_2026'

# ==============================================================================
# MANEJADORES DE ERRORES GLOBALES (Captura de Excepciones)
# ==============================================================================
@app.errorhandler(403)
def acceso_prohibido(error):
    """
    Ataja el error HTTP 403 Forbidden en cualquier Blueprint 
    y muestra la interfaz amigable de Baum.
    """
    return render_template('403.html'), 403


# ==============================================================================
# REGISTRO DE BLUEPRINTS (Orquestación Modular)
# ==============================================================================
app.register_blueprint(auth_bp)
app.register_blueprint(locales_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(precios_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(grupos_bp)

if __name__ == '__main__':
    # Tu app pasa de 583 líneas a menos de 20. ¡Una hermosura!
    app.run(debug=True, port=5000)