# language: es
Característica: Gestión de tareas
  Como usuario del sistema
  Quiero crear, consultar y cambiar el estado de mis tareas
  Para organizar mi trabajo de forma efectiva

  Escenario: Crear una tarea con datos válidos
    Dado que tengo la API de tareas disponible
    Cuando envío una solicitud para crear una tarea con título "Preparar presentación" y prioridad "alta"
    Entonces la respuesta debe tener código 201
    Y la tarea creada debe tener estado "pendiente"
    Y la tarea creada debe tener prioridad "alta"

  Escenario: Intentar crear una tarea sin título
    Dado que tengo la API de tareas disponible
    Cuando envío una solicitud para crear una tarea sin título
    Entonces la respuesta debe tener código 422
    Y la respuesta debe contener errores de validación

  Escenario: Intentar crear una tarea con prioridad inválida
    Dado que tengo la API de tareas disponible
    Cuando envío una solicitud para crear una tarea con título "Tarea X" y prioridad "urgente"
    Entonces la respuesta debe tener código 422
    Y la respuesta debe contener errores de validación

  Escenario: Completar una tarea pendiente
    Dado que tengo la API de tareas disponible
    Y existe una tarea pendiente con título "Tarea a completar"
    Cuando cambio el estado de esa tarea a "completada"
    Entonces la respuesta debe tener código 200
    Y la tarea debe tener estado "completada"

  Escenario: No se puede completar una tarea cancelada
    Dado que tengo la API de tareas disponible
    Y existe una tarea pendiente con título "Tarea cancelada"
    Y cambio el estado de esa tarea a "cancelada"
    Cuando intento cambiar el estado de esa tarea a "completada"
    Entonces la respuesta debe tener código 409

  Escenario: Consultar una tarea inexistente
    Dado que tengo la API de tareas disponible
    Cuando consulto la tarea con ID 99999
    Entonces la respuesta debe tener código 404
