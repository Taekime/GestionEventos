import unittest
from validador_evento import ValidadorEvento

class TestValidadorNombre(unittest.TestCase):

    def test_nombre_valido(self):
        """Debe devolver True si el nombre es una cadena no vacía"""
        self.assertTrue(ValidadorEvento.validar_nombre("Concierto Anual"))

    def test_nombre_vacio(self):
        """Debe devolver False si el nombre está vacío"""
        self.assertFalse(ValidadorEvento.validar_nombre(""))

    def test_nombre_espacios(self):
        """Debe devolver False si el nombre solo tiene espacios"""
        self.assertFalse(ValidadorEvento.validar_nombre("   "))

    def test_nombre_no_es_string(self):
        """Debe devolver False si el nombre no es un string"""
        self.assertFalse(ValidadorEvento.validar_nombre(1234))
        self.assertFalse(ValidadorEvento.validar_nombre(None))

if __name__ == "__main__":
    unittest.main() # pragma: no cover
