from flask import Blueprint, request, jsonify, current_app
from .services import validate_task_data, validate_status_transition, ValidationError, BusinessRuleError
from .database import get_db as _get_db

bp = Blueprint("tasks", __name__, url_prefix="/tasks")


def get_db():
    return _get_db(current_app._get_current_object())


def row_to_dict(row):
    return dict(row) if row else None


# ── GET /tasks ────────────────────────────────────────────────────────────────
@bp.route("", methods=["GET"])
def list_tasks():
    """Lista todas las tareas. Acepta ?status=pendiente|completada|cancelada"""
    db = get_db()
    status_filter = request.args.get("status")

    if status_filter:
        rows = db.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC",
            (status_filter,)
        ).fetchall()
    else:
        rows = db.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC"
        ).fetchall()

    return jsonify([row_to_dict(r) for r in rows]), 200


# ── POST /tasks ───────────────────────────────────────────────────────────────
@bp.route("", methods=["POST"])
def create_task():
    """Crea una nueva tarea. Aplica validaciones de negocio."""
    data = request.get_json(silent=True) or {}

    try:
        clean = validate_task_data(data)
    except ValidationError as e:
        return jsonify({"errors": e.args[0]}), 422

    db = get_db()
    cursor = db.execute(
        """INSERT INTO tasks (title, description, priority, due_date)
           VALUES (?, ?, ?, ?)""",
        (clean["title"], clean["description"], clean["priority"], clean["due_date"])
    )
    db.commit()

    task = row_to_dict(db.execute(
        "SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)
    ).fetchone())

    return jsonify(task), 201


# ── GET /tasks/<id> ───────────────────────────────────────────────────────────
@bp.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    """Obtiene una tarea por ID."""
    db = get_db()
    task = row_to_dict(db.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone())

    if not task:
        return jsonify({"error": "Tarea no encontrada."}), 404

    return jsonify(task), 200


# ── PATCH /tasks/<id>/status ──────────────────────────────────────────────────
@bp.route("/<int:task_id>/status", methods=["PATCH"])
def update_status(task_id):
    """Cambia el estado de una tarea. Aplica reglas de transición."""
    db = get_db()
    task = row_to_dict(db.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone())

    if not task:
        return jsonify({"error": "Tarea no encontrada."}), 404

    data = request.get_json(silent=True) or {}
    new_status = data.get("status", "").strip()

    try:
        validate_status_transition(task["status"], new_status)
    except ValidationError as e:
        return jsonify({"errors": e.args[0]}), 422
    except BusinessRuleError as e:
        return jsonify({"error": str(e)}), 409

    db.execute(
        "UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id)
    )
    db.commit()

    updated = row_to_dict(db.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone())

    return jsonify(updated), 200


# ── DELETE /tasks/<id> ────────────────────────────────────────────────────────
@bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Elimina una tarea por ID."""
    db = get_db()
    task = db.execute(
        "SELECT id FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    if not task:
        return jsonify({"error": "Tarea no encontrada."}), 404

    db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()

    return jsonify({"message": "Tarea eliminada correctamente."}), 200
