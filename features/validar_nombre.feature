Feature: Validación de nombres de eventos
  To ensure that registered events have correct names
  As an event management system
  I want to verify that the event name is a valid, non-empty string

  Scenario: Valid name
    Given the user enters the name "Festival de Música 2025"
    When the system validates the event name
    Then the validation should succeed and return True

  Scenario: Invalid name (empty or spaces)
    Given the user enters the name "    "
    When the system validates the event name
    Then the validation should fail and return False