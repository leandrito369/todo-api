"""
Pruebas de INTEGRACIÓN — Consigna 5b
======================================
Testean circuitos operativos completos a través de la API HTTP real:
POST → GET → PATCH → DELETE.
Usan el cliente de prueba de Flask con base de datos en memoria.
"""
import pytest
import json
from datetime import date, timedelta


TOMORROW = (date.today() + timedelta(days=1)).isoformat()


# ── Circuito 1: Ciclo de vida completo de una tarea ──────────────────────────

class TestCicloDeVidaTarea:
    """
    Circuito: Crear → Consultar → Completar → Verificar estado final.
    Representa el flujo más común de uso del sistema.
    """

    def test_crear_tarea_retorna_201(self, client):
        """POST /tasks con datos válidos debe retornar 201 y la tarea creada."""
        resp = client.post("/tasks", json={
            "title": "Estudiar para el parcial",
            "priority": "alta",
            "due_date": TOMORROW,
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "Estudiar para el parcial"
        assert data["priority"] == "alta"
        assert data["status"] == "pendiente"
        assert "id" in data

    def test_obtener_tarea_creada(self, client):
        """GET /tasks/<id> debe retornar la tarea previamente creada."""
        # Crear
        create_resp = client.post("/tasks", json={"title": "Hacer ejercicio"})
        task_id = create_resp.get_json()["id"]

        # Consultar
        get_resp = client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 200
        assert get_resp.get_json()["id"] == task_id

    def test_completar_tarea_pendiente(self, client):
        """PATCH /tasks/<id>/status a 'completada' debe funcionar desde 'pendiente'."""
        task_id = client.post("/tasks", json={"title": "Lavar el auto"}).get_json()["id"]

        resp = client.patch(f"/tasks/{task_id}/status", json={"status": "completada"})
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "completada"

    def test_eliminar_tarea_retorna_200(self, client):
        """DELETE /tasks/<id> debe eliminar la tarea y retornar 200."""
        task_id = client.post("/tasks", json={"title": "Tarea a eliminar"}).get_json()["id"]

        del_resp = client.delete(f"/tasks/{task_id}")
        assert del_resp.status_code == 200

        # Verificar que ya no existe
        get_resp = client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 404

    def test_flujo_completo_crear_listar_completar(self, client):
        """
        Circuito completo: POST → GET (lista) → PATCH (completar) → GET (verificar).
        Valida que el estado persiste correctamente en la DB en memoria.
        """
        # 1. Crear
        task = client.post("/tasks", json={
            "title": "Rendir el final",
            "priority": "alta",
        }).get_json()
        task_id = task["id"]

        # 2. Aparece en la lista general
        lista = client.get("/tasks").get_json()
        ids_en_lista = [t["id"] for t in lista]
        assert task_id in ids_en_lista

        # 3. Completar
        client.patch(f"/tasks/{task_id}/status", json={"status": "completada"})

        # 4. Aparece en el filtro ?status=completada
        completadas = client.get("/tasks?status=completada").get_json()
        ids_completadas = [t["id"] for t in completadas]
        assert task_id in ids_completadas

        # 5. No aparece en el filtro ?status=pendiente
        pendientes = client.get("/tasks?status=pendiente").get_json()
        ids_pendientes = [t["id"] for t in pendientes]
        assert task_id not in ids_pendientes


# ── Circuito 2: Manejo de errores y reglas de negocio ────────────────────────

class TestReglasDeNegocioViaAPI:
    """
    Circuito: Casos donde la API debe rechazar operaciones inválidas.
    """

    def test_crear_sin_titulo_retorna_422(self, client):
        """POST sin título debe retornar 422 Unprocessable Entity."""
        resp = client.post("/tasks", json={"priority": "alta"})
        assert resp.status_code == 422
        assert "errors" in resp.get_json()

    def test_completar_tarea_cancelada_retorna_409(self, client):
        """Intentar completar una tarea cancelada debe retornar 409 Conflict."""
        # Crear y cancelar
        task_id = client.post("/tasks", json={"title": "Tarea conflicto"}).get_json()["id"]
        client.patch(f"/tasks/{task_id}/status", json={"status": "cancelada"})

        # Intentar completar → debe fallar
        resp = client.patch(f"/tasks/{task_id}/status", json={"status": "completada"})
        assert resp.status_code == 409
        assert "error" in resp.get_json()

    def test_tarea_inexistente_retorna_404(self, client):
        """GET /tasks/9999 con ID inexistente debe retornar 404."""
        resp = client.get("/tasks/9999")
        assert resp.status_code == 404

    def test_eliminar_tarea_inexistente_retorna_404(self, client):
        """DELETE /tasks/9999 con ID inexistente debe retornar 404."""
        resp = client.delete("/tasks/9999")
        assert resp.status_code == 404
