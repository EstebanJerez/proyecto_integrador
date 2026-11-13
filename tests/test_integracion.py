"""Pruebas de integración A + B + C (flujo completo).

MATERIAL DE APOYO de la revisión docente. Estas pruebas NO hacen parte de la
evaluación de las semanas 10-12; sirven como ejemplo para la semana 14.
"""
import io
import unittest
from pathlib import Path

from src.services.datalab_service import ejecutar_archivo, ejecutar_demo

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# (archivo, filas, válidos, inválidos, errores técnicos) con los datasets actuales.
ESPERADO = [
    ("temperatura.csv", 623, 528, 91, 4),
    ("presion.json", 708, 595, 107, 6),
    ("humedad.xlsx", 573, 433, 131, 9),
]


class IntegracionTests(unittest.TestCase):
    def test_demo_en_memoria(self):
        r = ejecutar_demo()
        self.assertEqual(set(r), {"registros_validos", "registros_invalidos", "errores", "resumen"})
        self.assertEqual(r["resumen"]["total"], 12)
        self.assertEqual((r["resumen"]["bajos"], r["resumen"]["normales"], r["resumen"]["altos"]), (3, 6, 3))

    def test_tres_datasets_completos(self):
        for nombre, filas, validos, invalidos, errores in ESPERADO:
            archivo = io.BytesIO((RAW / nombre).read_bytes())
            r = ejecutar_archivo(archivo, nombre)
            conteo = (len(r["registros_validos"]), len(r["registros_invalidos"]), len(r["errores"]))
            self.assertEqual(conteo, (validos, invalidos, errores), nombre)
            # Ningún registro se pierde: cada fila cae en una sola bandeja.
            self.assertEqual(sum(conteo), filas, nombre)
            self.assertEqual(r["resumen"]["total"], validos)

    def test_validos_listos_para_la_interfaz(self):
        r = ejecutar_archivo(io.BytesIO((RAW / "presion.json").read_bytes()), "presion.json")
        for registro in r["registros_validos"]:
            self.assertIsInstance(registro["valor"], float)
            self.assertIn(registro["clasificacion"], {"BAJO", "NORMAL", "ALTO"})


if __name__ == "__main__":
    unittest.main()
