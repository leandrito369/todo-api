from app import create_app


def before_all(context):
    """Inicializa la app Flask en modo testing antes de todos los escenarios."""
    context.app = create_app(testing=True)
    context.client = context.app.test_client()
    context.app_context = context.app.app_context()
    context.app_context.push()


def after_all(context):
    """Limpia el contexto de la app al finalizar."""
    context.app_context.pop()
