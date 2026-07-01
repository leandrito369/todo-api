from datetime import date


VALID_PRIORITIES = {"alta", "media", "baja"}
VALID_STATUSES = {"pendiente", "completada", "cancelada"}


class ValidationError(Exception):
    """Se lanza cuando los datos de entrada no cumplen las reglas de negocio."""
    pass


class BusinessRuleError(Exception):
    """Se lanza cuando una operación viola una regla de negocio."""
    pass


def validate_task_data(data):
    """
    Valida los datos de una tarea antes de crearla o actualizarla.

    Reglas:
    - El título es obligatorio y no puede estar vacío.
    - La prioridad debe ser 'alta', 'media' o 'baja'.
    - La fecha de vencimiento no puede ser una fecha pasada.

    Retorna un dict con los campos saneados.
    Lanza ValidationError si alguna regla no se cumple.
    """
    errors = []

    # Regla 1: título obligatorio
    title = data.get("title", "").strip()
    if not title:
        errors.append("El título es obligatorio y no puede estar vacío.")

    # Regla 2: prioridad válida
    priority = data.get("priority", "media").strip().lower()
    if priority not in VALID_PRIORITIES:
        errors.append(
            f"La prioridad '{priority}' no es válida. "
            f"Debe ser una de: {', '.join(sorted(VALID_PRIORITIES))}."
        )

    # Regla 3: fecha de vencimiento no puede ser pasada
    due_date_str = data.get("due_date", None)
    if due_date_str:
        try:
            due_date = date.fromisoformat(due_date_str)
            if due_date < date.today():
                errors.append(
                    "La fecha de vencimiento no puede ser una fecha pasada."
                )
        except ValueError:
            errors.append(
                "El formato de fecha es inválido. Use YYYY-MM-DD."
            )

    if errors:
        raise ValidationError(errors)

    return {
        "title": title,
        "description": data.get("description", "").strip(),
        "priority": priority,
        "due_date": due_date_str,
    }


def validate_status_transition(current_status, new_status):
    """
    Valida que la transición de estado sea permitida.

    Reglas:
    - No se puede completar una tarea que ya está cancelada.
    - No se puede cancelar una tarea que ya está completada.
    - No se puede cambiar el estado de una tarea ya completada o cancelada
      a 'pendiente'.

    Lanza BusinessRuleError si la transición no es válida.
    """
    if new_status not in VALID_STATUSES:
        raise ValidationError(
            [f"Estado '{new_status}' no válido. Use: pendiente, completada, cancelada."]
        )

    if current_status == "cancelada" and new_status == "completada":
        raise BusinessRuleError(
            "No se puede completar una tarea que ya fue cancelada."
        )

    if current_status == "completada" and new_status == "cancelada":
        raise BusinessRuleError(
            "No se puede cancelar una tarea que ya fue completada."
        )

    if current_status in {"completada", "cancelada"} and new_status == "pendiente":
        raise BusinessRuleError(
            f"No se puede revertir una tarea '{current_status}' a 'pendiente'."
        )
