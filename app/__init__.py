from flask import Flask
from .database import init_db


def create_app(testing=False):
    app = Flask(__name__)

    if testing:
        app.config["TESTING"] = True
        app.config["DATABASE"] = ":memory:"
    else:
        app.config["DATABASE"] = "todo.db"

    init_db(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
