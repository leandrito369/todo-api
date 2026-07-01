from flask import Flask, jsonify
from .database import init_db

# TODO: reemplazar por tu nombre completo (consigna 3a del TP8)
AUTOR = "Leandro Lobayan"


def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config["TESTING"] = True
        app.config["DATABASE"] = ":memory:"
    else:
        app.config["DATABASE"] = "todo.db"

    init_db(app)

    # Habilita CORS para que el frontend (Netlify) pueda consumir esta API
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    @app.route("/")
    def index():
        return jsonify({
            "api": "todo-api",
            "descripcion": f"API REST de gestión de tareas — Trabajo Práctico de {AUTOR}",
            "autor": AUTOR,
            "version": "1.0",
            "endpoints": ["/tasks", "/tasks/<id>", "/tasks/<id>/status"]
        })

    from .routes import bp
    app.register_blueprint(bp)

    return app
