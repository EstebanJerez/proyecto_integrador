"""Rol C: lectores de archivos. Implementación del estudiante en semana 12.

Contrato de salida para cada lector: list[dict] con claves id, tipo, valor, unidad.
Los lectores no normalizan ni clasifican: entregan datos crudos al servicio.

REVISIÓN (semana 12):
  - Faltaba "import csv": leer_csv fallaba siempre con NameError.
  - Todos los imports se movieron al inicio del archivo (PEP 8).
  - Los lectores ahora aceptan cualquiera de estas entradas:
        * una ruta ("data/raw/temperatura.csv" o un Path),
        * un archivo abierto o el archivo que entrega Streamlit (UploadedFile),
        * bytes,
        * el diccionario {nombre: bytes} que usaba el estudiante.
    Antes leer_csv solo aceptaba rutas y leer_json no aceptaba el archivo de
    Streamlit, por eso la interfaz no podía cargar CSV ni JSON.
  - Se verifica la ESTRUCTURA (columnas id, tipo, valor, unidad) y se
    reportan los problemas con las excepciones del Rol B
    (ErrorFormatoFuente / ErrorLecturaFuente) en lugar de errores genéricos.
  - Una fila irregular NO detiene la lectura: se entrega marcada con
    "_error_tecnico" para que el procesamiento la registre como error.
  - Excel: las celdas vacías llegan como "" (igual que en CSV y JSON) y el
    texto "NA" ya no se convierte en NaN. Salida homogénea entre formatos.
"""
import csv
import io
import json
from pathlib import Path

import pandas as pd

from src.exceptions.errores import ErrorFormatoFuente, ErrorLecturaFuente

COLUMNAS_REQUERIDAS = ["id", "tipo", "valor", "unidad"]


# --- Funciones auxiliares (privadas: empiezan con "_") -----------------------

def _obtener_bytes(archivo):
    """Devuelve el contenido del archivo como bytes, sin importar cómo llegó."""
    try:
        if isinstance(archivo, (str, Path)):
            return Path(archivo).read_bytes()
        if isinstance(archivo, bytes):
            return archivo
        if isinstance(archivo, dict):
            # Forma usada por el estudiante: {"nombre.json": b"..."}
            return list(archivo.values())[0]
        if hasattr(archivo, "getvalue"):
            # UploadedFile de Streamlit y BytesIO: getvalue() devuelve todo el
            # contenido aunque alguien ya haya leído una parte.
            return archivo.getvalue()
        if hasattr(archivo, "read"):
            return archivo.read()
    except OSError as exc:
        raise ErrorLecturaFuente(f"No fue posible abrir el archivo: {exc}") from exc
    raise ErrorFormatoFuente(f"Tipo de entrada no soportado: {type(archivo).__name__}")


def _obtener_texto(archivo):
    """Contenido como texto UTF-8 (utf-8-sig elimina el BOM de Excel/Windows)."""
    try:
        return _obtener_bytes(archivo).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ErrorLecturaFuente("El archivo no está codificado en UTF-8") from exc


def _verificar_columnas(columnas, origen):
    """Lanza ErrorFormatoFuente si falta alguna columna del contrato."""
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in columnas]
    if faltantes:
        raise ErrorFormatoFuente(
            f"{origen}: faltan las columnas obligatorias {faltantes}"
        )


def _fila_irregular(origen, numero_fila, mensaje, identificador=None):
    """Registro marcado para que el Rol B lo reporte como error técnico."""
    return {
        "id": identificador,
        "_error_tecnico": mensaje,
        "_origen": origen,
        "_fila": numero_fila,
    }


# --- Lectores públicos (contrato) -------------------------------------------

def leer_csv(archivo):
    # TODO C-S12-01: leer CSV y devolver lista de diccionarios.
    texto = _obtener_texto(archivo)
    if texto.strip() == "":
        raise ErrorFormatoFuente("El archivo CSV está vacío")

    lector = csv.DictReader(io.StringIO(texto))
    _verificar_columnas(lector.fieldnames or [], "CSV")

    lista_diccionarios = []
    # start=2 porque la fila 1 del archivo es el encabezado.
    for numero_fila, fila in enumerate(lector, start=2):
        # DictReader guarda las celdas sobrantes en la clave None y pone
        # None en las columnas que faltan: ambas señales = fila irregular.
        if None in fila or None in fila.values():
            lista_diccionarios.append(_fila_irregular(
                "CSV", numero_fila, "Fila irregular: cantidad de columnas incorrecta",
                fila.get("id"),
            ))
            continue
        lista_diccionarios.append(dict(fila))
    return lista_diccionarios


def leer_json(archivo):
    # TODO C-S12-02: leer JSON y devolver lista de diccionarios.
    texto = _obtener_texto(archivo)
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise ErrorLecturaFuente(f"JSON mal formado: {exc.msg} (línea {exc.lineno})") from exc

    # Se acepta una lista de registros o {"registros": [...]}.
    if isinstance(datos, dict) and isinstance(datos.get("registros"), list):
        datos = datos["registros"]
    if not isinstance(datos, list):
        raise ErrorFormatoFuente("El JSON debe contener una lista de registros")

    lista_diccionarios = []
    for posicion, elemento in enumerate(datos, start=1):
        if not isinstance(elemento, dict):
            lista_diccionarios.append(_fila_irregular(
                "JSON", posicion, "Elemento que no es un objeto JSON"
            ))
            continue
        lista_diccionarios.append(elemento)
    return lista_diccionarios


def leer_excel(archivo):
    # TODO C-S12-03: leer Excel y devolver lista de diccionarios.
    try:
        df = pd.read_excel(
            io.BytesIO(_obtener_bytes(archivo)),
            dtype=object,            # no forzar tipos: el Rol A decide
            keep_default_na=False,   # "NA" sigue siendo texto y lo vacío es ""
        )
    except (ErrorFormatoFuente, ErrorLecturaFuente):
        raise
    except Exception as exc:  # noqa: BLE001 - pandas/openpyxl lanzan varios tipos
        raise ErrorLecturaFuente(f"No fue posible leer el Excel: {exc}") from exc

    # Los encabezados se comparan como texto ("id", "tipo"...).
    df.columns = [str(c) for c in df.columns]
    _verificar_columnas(list(df.columns), "Excel")
    return df.to_dict(orient="records")
