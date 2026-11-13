"""Rol C: selección y unificación de fuentes.

REVISIÓN (semana 12):
  - Si no se entrega nombre_archivo se intenta obtener de archivo.name
    (Streamlit y los archivos abiertos lo tienen) o de la propia ruta.
  - Una extensión no soportada lanza ErrorFormatoFuente (contrato de
    excepciones del Rol B) en lugar de ValueError.
  - Se quitó ".xls": el proyecto solo instala openpyxl, que lee .xlsx.
    Aceptar .xls prometía algo que fallaba al leer.
  - Un diccionario de lectores reemplaza la cadena de if. Este es el ÚNICO
    lugar del proyecto que decide qué lector usar.
"""
from pathlib import Path

from src.data.fuentes_memoria import cargar_desde_memoria
from src.data.lectores import leer_csv, leer_excel, leer_json
from src.exceptions.errores import ErrorFormatoFuente

LECTORES_POR_EXTENSION = {
    "csv": leer_csv,
    "json": leer_json,
    "xlsx": leer_excel,
}


def _nombre_de(archivo, nombre_archivo):
    if nombre_archivo:
        return str(nombre_archivo)
    if isinstance(archivo, (str, Path)):
        return str(archivo)
    return str(getattr(archivo, "name", ""))


def cargar_datos(archivo=None, nombre_archivo=""):
    """Carga memoria o delega al lector según extensión."""
    if archivo is None:
        return cargar_desde_memoria()

    nombre = _nombre_de(archivo, nombre_archivo)
    extension = Path(nombre).suffix.lower().lstrip(".")
    lector = LECTORES_POR_EXTENSION.get(extension)
    if lector is None:
        raise ErrorFormatoFuente(
            f"Extensión no soportada: '{extension or 'sin extensión'}'. "
            f"Use {', '.join(LECTORES_POR_EXTENSION)}"
        )
    return lector(archivo)
