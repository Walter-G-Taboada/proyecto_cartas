from flask import Flask
from routes.auth import auth_bp
from routes.locales import locales_bp
from routes.productos import productos_bp
from routes.precios import precios_bp

app = Flask(__name__)
app.secret_key = 'baum_secret_key_2026'

# ==============================================================================
# REGISTRO DE BLUEPRINTS (Orquestación Modular)
# ==============================================================================
app.register_blueprint(auth_bp)
app.register_blueprint(locales_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(precios_bp)

if __name__ == '__main__':
    # Tu app pasa de 583 líneas a menos de 20. ¡Una hermosura!
    app.run(debug=True, port=5000)