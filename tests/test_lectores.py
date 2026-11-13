"""Pruebas del Rol C (fuentes y lectores).

MATERIAL DE APOYO de la revisión docente. Estas pruebas NO hacen parte de la
evaluación de las semanas 10-12; sirven como ejemplo para la semana 14.
"""
import io
import unittest
from pathlib import Path

from src.data.carga_datos import cargar_datos
from src.data.fuentes_memoria import cargar_desde_memoria, preparar_registros_prueba
from src.data.lectores import leer_csv, leer_excel, leer_json
from src.exceptions.errores import ErrorFormatoFuente, ErrorLecturaFuente

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
CLAVES = {"id", "tipo", "valor", "unidad"}


class MemoriaTests(unittest.TestCase):
    def test_doce_registros_base_y_listas_nuevas(self):
        a = cargar_desde_memoria()
        a[0]["valor"] = -1
        self.assertEqual(len(cargar_desde_memoria()), 12)
        self.assertNotEqual(cargar_desde_memoria()[0]["valor"], -1)

    def test_registros_prueba_no_repiten_ids_base(self):
        base = {r["id"] for r in cargar_desde_memoria()}
        prueba = {r.get("id") for r in preparar_registros_prueba()}
        self.assertFalse(base & prueba)


class DatasetsTests(unittest.TestCase):
    """Los tres datasets se cargan con el contrato común (aceptación S12)."""

    def test_tres_datasets_por_ruta(self):
        for nombre, filas in [("temperatura.csv", 623), ("presion.json", 708), ("humedad.xlsx", 573)]:
            registros = cargar_datos(RAW / nombre)
            self.assertEqual(len(registros), filas, nombre)
            self.assertTrue(all(CLAVES <= set(r) for r in registros), nombre)

    def test_archivo_en_memoria_como_streamlit(self):
        # Streamlit entrega un objeto tipo BytesIO con atributo .name
        for nombre in ["temperatura.csv", "presion.json", "humedad.xlsx"]:
            archivo = io.BytesIO((RAW / nombre).read_bytes())
            archivo.name = nombre
            self.assertGreater(len(cargar_datos(archivo)), 0, nombre)

    def test_excel_sin_nan(self):
        for r in leer_excel(RAW / "humedad.xlsx"):
            valor = r["valor"]
            self.assertFalse(isinstance(valor, float) and valor != valor)


class CsvTests(unittest.TestCase):
    def test_fila_irregular_no_detiene_lectura(self):
        datos = b"id,tipo,valor,unidad\nT1,temperatura,20,\xc2\xb0C\nT2,temperatura\nT3,temperatura,21,\xc2\xb0C\n"
        filas = leer_csv(datos)
        self.assertEqual(len(filas), 3)
        self.assertEqual(filas[1]["_error_tecnico"].split(":")[0], "Fila irregular")
        self.assertEqual(filas[1]["_fila"], 3)

    def test_solo_encabezado_es_lista_vacia(self):
        self.assertEqual(leer_csv(b"id,tipo,valor,unidad\n"), [])

    def test_vacio_o_sin_columnas(self):
        with self.assertRaises(ErrorFormatoFuente):
            leer_csv(b"")
        with self.assertRaises(ErrorFormatoFuente):
            leer_csv(b"codigo,medida\n1,2\n")


class JsonTests(unittest.TestCase):
    def test_lista_y_objeto_con_registros(self):
        self.assertEqual(len(leer_json(b'[{"id": "P1"}]')), 1)
        self.assertEqual(len(leer_json(b'{"registros": [{"id": "P1"}]}')), 1)

    def test_estructuras_inesperadas(self):
        with self.assertRaises(ErrorLecturaFuente):
            leer_json(b"{")
        with self.assertRaises(ErrorFormatoFuente):
            leer_json(b'{"id": "P1"}')
        self.assertIn("_error_tecnico", leer_json(b'[1]')[0])


class CargaDatosTests(unittest.TestCase):
    def test_sin_archivo_usa_memoria(self):
        self.assertEqual(len(cargar_datos()), 12)

    def test_extension_no_soportada(self):
        with self.assertRaises(ErrorFormatoFuente):
            cargar_datos(b"x", "datos.xls")


if __name__ == "__main__":
    unittest.main()
