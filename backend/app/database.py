import sqlite3
from flask import g

CREATE_TASKS_TABLE = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT NOT NULL DEFAULT 'media',
        status TEXT NOT NULL DEFAULT 'pendiente',
        due_date TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
"""


def _connect(app):
    """Abre una nueva conexión a la base de datos configurada en la app."""
    conn = sqlite3.connect(
        app.config["DATABASE"],
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    conn.row_factory = sqlite3.Row
    return conn


def get_db(app):
    """Retorna la conexión del contexto actual, creándola si no existe."""
    if "db" not in g:
        g.db = _connect(app)
        # Para :memory: la tabla debe existir en esta misma conexión
        g.db.execute(CREATE_TASKS_TABLE)
        g.db.commit()
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Registra el teardown y, para DBs en archivo, crea la tabla al inicio."""
    app.teardown_appcontext(close_db)

    if app.config["DATABASE"] != ":memory:":
        with app.app_context():
            conn = _connect(app)
            conn.execute(CREATE_TASKS_TABLE)
            conn.commit()
            conn.close()
