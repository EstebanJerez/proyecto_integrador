"""Rol B: excepciones y registro de incidencias (Versión simplificada)."""
from datetime import datetime


class DataLabError(Exception):
    """Excepción base de la aplicación."""
    pass


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""
    pass


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""
    pass


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""
    pass


def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    """Crea un diccionario normalizado con los datos del error."""
    return {
        "timestamp": datetime.now().isoformat(),
        "origen": origen,
        "identificador": identificador,
        "categoria": categoria,
        "mensaje": str(mensaje),
    }