"""
Pruebas UNITARIAS — Consigna 5a
================================
Testean la lógica de negocio pura en app/services.py,
sin levantar la app Flask ni tocar la base de datos.
"""
import pytest
from datetime import date, timedelta
from app.services import (
    validate_task_data,
    validate_status_transition,
    ValidationError,
    BusinessRuleError,
)


# ── validate_task_data ────────────────────────────────────────────────────────

class TestValidateTaskData:

    def test_datos_validos_retorna_dict_saneado(self):
        """Con datos correctos debe retornar el dict limpio."""
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        data = {
            "title": "  Comprar leche  ",
            "description": "En el súper",
            "priority": "ALTA",
            "due_date": tomorrow,
        }
        result = validate_task_data(data)
        assert result["title"] == "Comprar leche"
        assert result["priority"] == "alta"
        assert result["due_date"] == tomorrow

    def test_titulo_vacio_lanza_error(self):
        """El título vacío debe lanzar ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_task_data({"title": "   "})
        errores = exc_info.value.args[0]
        assert any("título" in e for e in errores)

    def test_titulo_ausente_lanza_error(self):
        """Sin clave 'title' debe lanzar ValidationError."""
        with pytest.raises(ValidationError):
            validate_task_data({})

    def test_prioridad_invalida_lanza_error(self):
        """Una prioridad fuera del rango válido debe lanzar ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_task_data({"title": "Tarea", "priority": "urgente"})
        errores = exc_info.value.args[0]
        assert any("prioridad" in e.lower() for e in errores)

    def test_fecha_pasada_lanza_error(self):
        """Una fecha de vencimiento en el pasado debe lanzar ValidationError."""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        with pytest.raises(ValidationError) as exc_info:
            validate_task_data({"title": "Tarea", "due_date": yesterday})
        errores = exc_info.value.args[0]
        assert any("pasada" in e for e in errores)

    def test_fecha_formato_invalido_lanza_error(self):
        """Una fecha con formato incorrecto debe lanzar ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_task_data({"title": "Tarea", "due_date": "31-12-2099"})
        errores = exc_info.value.args[0]
        assert any("formato" in e for e in errores)

    def test_sin_due_date_es_valido(self):
        """Una tarea sin fecha de vencimiento es completamente válida."""
        result = validate_task_data({"title": "Tarea sin fecha"})
        assert result["title"] == "Tarea sin fecha"
        assert result["due_date"] is None

    def test_prioridad_por_defecto_es_media(self):
        """Si no se especifica prioridad, debe asignarse 'media'."""
        result = validate_task_data({"title": "Tarea"})
        assert result["priority"] == "media"

    def test_multiples_errores_se_acumulan(self):
        """Título vacío Y prioridad inválida deben reportarse juntos."""
        with pytest.raises(ValidationError) as exc_info:
            validate_task_data({"title": "", "priority": "invalida"})
        errores = exc_info.value.args[0]
        assert len(errores) >= 2


# ── validate_status_transition ────────────────────────────────────────────────

class TestValidateStatusTransition:

    def test_pendiente_a_completada_es_valido(self):
        """Completar una tarea pendiente es una transición válida."""
        validate_status_transition("pendiente", "completada")  # no debe lanzar

    def test_pendiente_a_cancelada_es_valido(self):
        """Cancelar una tarea pendiente es una transición válida."""
        validate_status_transition("pendiente", "cancelada")  # no debe lanzar

    def test_cancelada_a_completada_lanza_business_error(self):
        """No se puede completar una tarea cancelada — regla de negocio."""
        with pytest.raises(BusinessRuleError) as exc_info:
            validate_status_transition("cancelada", "completada")
        assert "cancelada" in str(exc_info.value).lower()

    def test_completada_a_cancelada_lanza_business_error(self):
        """No se puede cancelar una tarea ya completada — regla de negocio."""
        with pytest.raises(BusinessRuleError) as exc_info:
            validate_status_transition("completada", "cancelada")
        assert "completada" in str(exc_info.value).lower()

    def test_completada_a_pendiente_lanza_business_error(self):
        """No se puede revertir una tarea completada a pendiente."""
        with pytest.raises(BusinessRuleError):
            validate_status_transition("completada", "pendiente")

    def test_estado_invalido_lanza_validation_error(self):
        """Un estado desconocido debe lanzar ValidationError."""
        with pytest.raises(ValidationError):
            validate_status_transition("pendiente", "en_progreso")
