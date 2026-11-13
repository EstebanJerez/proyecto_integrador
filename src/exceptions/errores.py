"""Rol B: excepciones y registro de incidencias.

REVISIÓN (semanas 11-12):
  - Cada excepción tiene ahora un atributo de clase CATEGORIA. Así el
    procesamiento no necesita una cadena de if/elif para saber la categoría:
    basta con leer error.CATEGORIA (las subclases la heredan o la cambian).
  - Se agregan ErrorConversion, ErrorEstructuraRegistro y ErrorTimeoutSensor,
    que la interfaz y las pruebas del docente esperan.
  - El reporte usa la clave "fecha_hora" (contrato de la interfaz docente),
    no "timestamp".
"""
from datetime import datetime


class DataLabError(Exception):
    """Excepción base de la aplicación."""
    CATEGORIA = "DATALAB"


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""
    CATEGORIA = "VALIDACION"


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado
    (extensión no soportada, columnas faltantes, JSON que no es una lista...)."""
    CATEGORIA = "FORMATO"


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos (archivo dañado, codificación...)."""
    CATEGORIA = "LECTURA"


# --- REVISIÓN: excepciones nuevas -------------------------------------------

class ErrorConversion(DataLabError):
    """Un valor que pasó la validación no se pudo convertir a número (semana 12)."""
    CATEGORIA = "CONVERSION"


class ErrorEstructuraRegistro(ErrorFormatoFuente):
    """Un registro individual llegó roto: no es diccionario o el lector lo
    marcó con la clave "_error_tecnico" (por ejemplo, una fila irregular del CSV).
    Hereda de ErrorFormatoFuente porque es un problema de estructura."""
    CATEGORIA = "ESTRUCTURA_REGISTRO"


class ErrorTimeoutSensor(DataLabError):
    """El sensor no respondió a tiempo. Se simula con la clave
    "observacion_tecnica": "SIMULACION_TIMEOUT_SENSOR"."""
    CATEGORIA = "TIMEOUT_SENSOR"


def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    """Crea un diccionario normalizado con los datos del error.

    Claves (contrato con la interfaz docente, pestaña "Errores técnicos"):
    identificador, categoria, origen, mensaje, fecha_hora.
    """
    return {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "origen": origen,
        "identificador": identificador,
        "categoria": categoria,
        "mensaje": str(mensaje),
    }
