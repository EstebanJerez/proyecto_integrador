"""Rol A: normalización y estandarización de registros.

SEMANA 10: implementar las funciones marcadas TODO.
Contrato: recibir un diccionario y devolver una COPIA normalizada.
No modificar el registro original.

REVISIÓN (semanas 10-12): se conserva el trabajo del estudiante y se agregan
tres estandarizaciones que la guía pide para el rol A ("normalizar
identificadores, tipos, unidades y valores"):
  - id en mayúsculas          ("p101"     -> "P101")
  - tipo sin tildes           ("Presión"  -> "presion")
  - unidad con forma oficial  ("HPA", "°c", "ºC" -> "hPa", "°C")
  - valor vacío de archivos   (NaN de Excel -> None)
  - coma decimal en texto     ("21,5"     -> "21.5")
"""
CAMPOS_A_LIMPIAR = ["id", "tipo", "unidad", "valor"]

# REVISIÓN: tabla de equivalencias de unidades. La clave es la unidad escrita
# en minúsculas y sin espacios; el valor es la forma oficial que espera
# validaciones.py. Así la validación compara siempre contra un único texto.
EQUIVALENCIAS_UNIDAD = {
    "°c": "°C",
    "ºc": "°C",   # "º" (indicador ordinal) se confunde a menudo con "°" (grado)
    "c": "°C",
    "celsius": "°C",
    "hpa": "hPa",
    "%": "%",
    "porcentaje": "%",
}

# REVISIÓN: vocales con tilde que pueden aparecer en el tipo ("presión").
SIN_TILDES = str.maketrans("áéíóúÁÉÍÓÚ", "aeiouAEIOU")


def _es_nan(dato):
    """True si el dato es un NaN (Not a Number).

    pandas usa NaN para las celdas vacías de Excel. Un NaN es el único valor
    que no es igual a sí mismo, por eso basta con comparar dato != dato.
    """
    return isinstance(dato, float) and dato != dato


def normalizar_registro(registro):
    # TODO A-S10-01: validar que registro sea un diccionario.

    if not isinstance(registro, dict): # isinstance pregunta "¿este dato es de tipo dict?".
        raise TypeError("el registro debe ser un diccionario")

    copia = registro.copy()

    # TODO A-S10-02: quitar espacios de id, tipo, unidad y valor textual.

    for campo in CAMPOS_A_LIMPIAR:

        if campo in copia and isinstance(copia[campo], str):
            copia[campo] = copia[campo].strip()

    # TODO A-S10-03: estandarizar tipo a minúsculas.

    if "tipo" in copia and isinstance(copia["tipo"], str):
        # REVISIÓN: además de minúsculas se quitan las tildes, porque
        # TIPOS_PERMITIDOS usa "presion" sin tilde.
        copia["tipo"] = copia["tipo"].lower().translate(SIN_TILDES)

    # REVISIÓN: el id se estandariza en mayúsculas ("t001" y "T001" son el
    # mismo sensor). Solo se toca si es texto; un id numérico se deja igual.
    if "id" in copia and isinstance(copia["id"], str):
        copia["id"] = copia["id"].upper()

    # REVISIÓN: la unidad se lleva a su forma oficial usando la tabla.
    # Si la unidad no está en la tabla se deja como llegó, y será la
    # validación la que explique el motivo del rechazo.
    if "unidad" in copia and isinstance(copia["unidad"], str):
        clave = copia["unidad"].lower().replace(" ", "")
        copia["unidad"] = EQUIVALENCIAS_UNIDAD.get(clave, copia["unidad"])

    # REVISIÓN: valores que llegan desde archivos.
    if "valor" in copia:
        # Una celda vacía de Excel llega como NaN; se convierte en None para
        # que la validación la reconozca como "campo faltante" igual que un
        # texto vacío del CSV o del JSON. Así la calidad NO depende del origen.
        if _es_nan(copia["valor"]):
            copia["valor"] = None
        # "21,5" (coma decimal) se deja como "21.5". Solo se reemplaza si hay
        # exactamente una coma y ningún punto, para no dañar textos raros.
        elif isinstance(copia["valor"], str):
            texto = copia["valor"]
            if texto.count(",") == 1 and "." not in texto:
                copia["valor"] = texto.replace(",", ".")

    # TODO A-S10-04: devolver una copia; no convertir aún el valor a float aquí.

    return copia
