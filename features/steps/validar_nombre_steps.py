from behave import given, when, then
from validador_evento import ValidadorEvento

# Paso: Given the user enters the name "..."
# Contexto: El usuario ingresa un nombre para el evento
@given('the user enters the name "{nombre}"')
def step_given_user_enters_name(context, nombre):
    context.nombre = nombre

# Paso: When the system validates the event name
# Contexto: El sistema valida el nombre del evento ingresado
@when('the system validates the event name')
def step_when_system_validates_name(context):
    context.resultado = ValidadorEvento.validar_nombre(context.nombre)

# Paso: Then the validation should succeed and return True
# Contexto: La validación debe ser exitosa y retornar True
@then('the validation should succeed and return True')
def step_then_validation_succeeds(context):
    assert context.resultado is True, f"Se esperaba True, pero se obtuvo {context.resultado}"

# Paso: Then the validation should fail and return False
# Contexto: La validación debe fallar y retornar False
@then('the validation should fail and return False')
def step_then_validation_fails(context):
    assert context.resultado is False, f"Se esperaba False, pero se obtuvo {context.resultado}"
