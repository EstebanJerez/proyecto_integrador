"""Pruebas del Rol A (calidad).

MATERIAL DE APOYO de la revisión docente. Estas pruebas NO hacen parte de la
evaluación de las semanas 10-12; sirven como ejemplo para la semana 14.
Ejecutar:  python -m unittest discover -s tests -v
"""
import unittest

from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro


class NormalizacionTests(unittest.TestCase):
    def test_devuelve_copia_sin_modificar_original(self):
        original = {"id": " t1 ", "tipo": " TEMPERATURA ", "valor": " 20 ", "unidad": " °c "}
        copia = normalizar_registro(original)
        self.assertIsNot(copia, original)
        self.assertEqual(original["tipo"], " TEMPERATURA ")

    def test_estandariza_id_tipo_unidad_y_valor(self):
        copia = normalizar_registro(
            {"id": " p101 ", "tipo": " Presión ", "valor": " 1013,2 ", "unidad": " HPA "}
        )
        self.assertEqual(copia, {"id": "P101", "tipo": "presion", "valor": "1013.2", "unidad": "hPa"})

    def test_no_convierte_valor_a_float(self):
        self.assertEqual(normalizar_registro({"valor": "21.5"})["valor"], "21.5")

    def test_nan_de_excel_se_vuelve_none(self):
        self.assertIsNone(normalizar_registro({"valor": float("nan")})["valor"])

    def test_rechaza_lo_que_no_es_diccionario(self):
        with self.assertRaises(TypeError):
            normalizar_registro(["T1", "temperatura", 20, "°C"])


class ValidacionTests(unittest.TestCase):
    def test_registro_correcto(self):
        self.assertEqual(
            validar_registro({"id": "T1", "tipo": "temperatura", "valor": "20", "unidad": "°C"}),
            (True, []),
        )

    def test_acumula_todos_los_motivos(self):
        ok, motivos = validar_registro({"id": "", "tipo": "otro", "valor": "x", "unidad": ""})
        self.assertFalse(ok)
        self.assertEqual(len(motivos), 4)

    def test_valores_no_numericos_de_los_datasets(self):
        for texto in ["N/A", "SIN_DATO", "ERROR_SENSOR", "nan", "inf"]:
            ok, motivos = validar_registro({"id": "T1", "tipo": "temperatura", "valor": texto, "unidad": "°C"})
            self.assertFalse(ok, texto)
            self.assertIn("no es numérico", motivos[0])

    def test_vacio_y_none_son_campo_faltante(self):
        for vacio in ["", "   ", None, float("nan")]:
            ok, motivos = validar_registro({"id": "T1", "tipo": "temperatura", "valor": vacio, "unidad": "°C"})
            self.assertEqual(motivos, ["falta el campo obligatorio: valor"])

    def test_unidad_incorrecta(self):
        ok, motivos = validar_registro({"id": "T1", "tipo": "temperatura", "valor": 20, "unidad": "unidad_desconocida"})
        self.assertFalse(ok)
        self.assertIn("unidad incorrecta", motivos[0])

    def test_rango_plausible_y_limites(self):
        casos = [
            ("temperatura", 999, False), ("temperatura", 50, True), ("temperatura", 50.01, False),
            ("presion", 650, False), ("presion", 800, True), ("presion", 1100, True),
            ("humedad", -5, False), ("humedad", 0, True), ("humedad", 100, True), ("humedad", 125, False),
        ]
        unidades = {"temperatura": "°C", "presion": "hPa", "humedad": "%"}
        for tipo, valor, esperado in casos:
            ok, _ = validar_registro({"id": "X1", "tipo": tipo, "valor": valor, "unidad": unidades[tipo]})
            self.assertEqual(ok, esperado, f"{tipo}={valor}")

    def test_booleano_no_es_medicion(self):
        ok, _ = validar_registro({"id": "T1", "tipo": "temperatura", "valor": True, "unidad": "°C"})
        self.assertFalse(ok)

    def test_tipo_no_textual_no_rompe(self):
        ok, motivos = validar_registro({"id": "T1", "tipo": ["temperatura"], "valor": 20, "unidad": "°C"})
        self.assertFalse(ok)
        self.assertIn("tipo no permitido", motivos[0])


if __name__ == "__main__":
    unittest.main()
