from behave import given, when, then
from datetime import date, timedelta

TOMORROW = (date.today() + timedelta(days=1)).isoformat()


# ── GIVEN ─────────────────────────────────────────────────────────────────────

@given("que tengo la API de tareas disponible")
def step_api_disponible(context):
    """El cliente ya está disponible desde environment.py."""
    assert context.client is not None


@given('existe una tarea pendiente con título "{titulo}"')
def step_existe_tarea(context, titulo):
    """Crea una tarea pendiente y guarda su ID en el contexto."""
    resp = context.client.post("/tasks", json={"title": titulo})
    assert resp.status_code == 201, f"No se pudo crear la tarea: {resp.get_json()}"
    context.task_id = resp.get_json()["id"]


@given('cambio el estado de esa tarea a "{nuevo_estado}"')
def step_dado_cambio_estado(context, nuevo_estado):
    """Cambia el estado de la tarea actual (usado en precondiciones)."""
    resp = context.client.patch(
        f"/tasks/{context.task_id}/status",
        json={"status": nuevo_estado}
    )
    assert resp.status_code == 200, f"Fallo al cambiar estado: {resp.get_json()}"


# ── WHEN ──────────────────────────────────────────────────────────────────────

@when('envío una solicitud para crear una tarea con título "{titulo}" y prioridad "{prioridad}"')
def step_crear_tarea_con_prioridad(context, titulo, prioridad):
    context.response = context.client.post("/tasks", json={
        "title": titulo,
        "priority": prioridad,
        "due_date": TOMORROW,
    })


@when("envío una solicitud para crear una tarea sin título")
def step_crear_tarea_sin_titulo(context):
    context.response = context.client.post("/tasks", json={
        "description": "Sin título"
    })


@when('cambio el estado de esa tarea a "{nuevo_estado}"')
def step_cambiar_estado(context, nuevo_estado):
    context.response = context.client.patch(
        f"/tasks/{context.task_id}/status",
        json={"status": nuevo_estado}
    )


@when('intento cambiar el estado de esa tarea a "{nuevo_estado}"')
def step_intentar_cambiar_estado(context, nuevo_estado):
    context.response = context.client.patch(
        f"/tasks/{context.task_id}/status",
        json={"status": nuevo_estado}
    )


@when("consulto la tarea con ID {task_id:d}")
def step_consultar_tarea(context, task_id):
    context.response = context.client.get(f"/tasks/{task_id}")


# ── THEN ──────────────────────────────────────────────────────────────────────

@then("la respuesta debe tener código {codigo:d}")
def step_verificar_codigo(context, codigo):
    actual = context.response.status_code
    assert actual == codigo, (
        f"Se esperaba código {codigo} pero se obtuvo {actual}. "
        f"Body: {context.response.get_json()}"
    )


@then('la tarea creada debe tener estado "{estado}"')
def step_verificar_estado_creada(context, estado):
    data = context.response.get_json()
    assert data["status"] == estado, f"Estado esperado '{estado}', obtenido '{data['status']}'"


@then('la tarea creada debe tener prioridad "{prioridad}"')
def step_verificar_prioridad_creada(context, prioridad):
    data = context.response.get_json()
    assert data["priority"] == prioridad, (
        f"Prioridad esperada '{prioridad}', obtenida '{data['priority']}'"
    )


@then("la respuesta debe contener errores de validación")
def step_verificar_errores_validacion(context):
    data = context.response.get_json()
    assert "errors" in data, f"Se esperaba 'errors' en la respuesta, pero se obtuvo: {data}"
    assert len(data["errors"]) > 0, "La lista de errores está vacía"


@then('la tarea debe tener estado "{estado}"')
def step_verificar_estado(context, estado):
    data = context.response.get_json()
    assert data["status"] == estado, f"Estado esperado '{estado}', obtenido '{data['status']}'"
