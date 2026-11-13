"""Pruebas del Rol B (robustez y errores).

MATERIAL DE APOYO de la revisión docente. Estas pruebas NO hacen parte de la
evaluación de las semanas 10-12; sirven como ejemplo para la semana 14.
"""
import unittest

from src.data.fuentes_memoria import preparar_escenarios_defectuosos
from src.exceptions.errores import (
    DataLabError,
    ErrorEstructuraRegistro,
    ErrorFormatoFuente,
    ErrorTimeoutSensor,
    crear_reporte_error,
)
from src.processing.procesamiento import procesar_archivo, procesar_registros

CLAVES_REPORTE = {"fecha_hora", "origen", "identificador", "categoria", "mensaje"}


class ExcepcionesTests(unittest.TestCase):
    def test_jerarquia(self):
        self.assertTrue(issubclass(ErrorEstructuraRegistro, ErrorFormatoFuente))
        self.assertTrue(issubclass(ErrorTimeoutSensor, DataLabError))

    def test_categoria_por_clase(self):
        self.assertEqual(ErrorTimeoutSensor.CATEGORIA, "TIMEOUT_SENSOR")
        self.assertEqual(ErrorEstructuraRegistro.CATEGORIA, "ESTRUCTURA_REGISTRO")

    def test_reporte_tiene_claves_del_contrato(self):
        reporte = crear_reporte_error("lote", "T1", ValueError("x"), "SISTEMA")
        self.assertEqual(set(reporte), CLAVES_REPORTE)
        self.assertEqual(reporte["mensaje"], "x")


class ContinuidadTests(unittest.TestCase):
    def test_escenarios_defectuosos_no_detienen_el_lote(self):
        r = procesar_registros(preparar_escenarios_defectuosos())
        self.assertEqual(len(r["registros_validos"]), 2)
        self.assertEqual(len(r["errores"]), 4)
        categorias = sorted(e["categoria"] for e in r["errores"])
        self.assertEqual(categorias, ["ESTRUCTURA_REGISTRO"] * 3 + ["TIMEOUT_SENSOR"])

    def test_cada_evento_simulado_tiene_su_categoria(self):
        eventos = {
            "SIMULACION_TIMEOUT_SENSOR": "TIMEOUT_SENSOR",
            "SIMULACION_PAQUETE_INCOMPLETO": "PAQUETE_INCOMPLETO",
            "SIMULACION_LECTURA_INTERMITENTE": "LECTURA_INTERMITENTE",
            "SIMULACION_OTRO_EVENTO": "EVENTO_SENSOR",
        }
        for evento, categoria in eventos.items():
            r = procesar_registros([{"id": "T1", "tipo": "temperatura", "valor": 20,
                                     "unidad": "°C", "observacion_tecnica": evento}])
            self.assertEqual(r["errores"][0]["categoria"], categoria)

    def test_observacion_vacia_no_es_error(self):
        r = procesar_registros([{"id": "T1", "tipo": "temperatura", "valor": 20,
                                 "unidad": "°C", "observacion_tecnica": ""}])
        self.assertEqual(len(r["registros_validos"]), 1)

    def test_entrada_que_no_es_lista(self):
        r = procesar_registros("no soy una lista")
        self.assertEqual(r["errores"][0]["categoria"], "FORMATO")
        self.assertEqual(r["resumen"]["total"], 0)

    def test_invalido_con_registro_y_motivos_separados(self):
        r = procesar_registros([{"id": "T1", "tipo": "temperatura", "valor": "N/A", "unidad": "°C"}])
        invalido = r["registros_invalidos"][0]
        self.assertEqual(set(invalido), {"registro", "motivos"})
        self.assertNotIn("motivos", invalido["registro"])

    def test_no_modifica_los_registros_de_entrada(self):
        entrada = [{"id": " t1 ", "tipo": "Temperatura", "valor": "20", "unidad": "°C"}]
        procesar_registros(entrada)
        self.assertEqual(entrada[0]["id"], " t1 ")


class ErroresDeArchivoTests(unittest.TestCase):
    def test_extension_no_soportada(self):
        r = procesar_archivo("datos.txt")
        self.assertEqual(r["errores"][0]["categoria"], "FORMATO")

    def test_archivo_inexistente(self):
        r = procesar_archivo("no_existe.csv")
        self.assertEqual(r["errores"][0]["categoria"], "LECTURA")
        self.assertEqual(r["registros_validos"], [])


if __name__ == "__main__":
    unittest.main()
