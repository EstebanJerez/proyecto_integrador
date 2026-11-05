"""Rol A: reglas de validación de calidad de registros.
 
Un registro es un diccionario con cuatro claves:
    {"id": "P001", "tipo": "presion", "valor": 295.5, "unidad": "hPa"}
 
Este módulo NO clasifica el valor (alto, bajo, normal...). Eso lo hace
clasificar_valor(valor, tipo) en clasificacion.py. Aquí solo revisamos que
el registro esté bien formado.
"""
 
# Tipos de sensor que aceptamos (un set sirve para preguntar "¿está aquí?").
TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}
 
# Unidad correcta para cada tipo de sensor.
# Clave = tipo, valor = unidad esperada.
# OJO: la de presión (hPa) sale de presion.json. Revisa que la de temperatura
# y la de humedad coincidan con temperatura.csv y humedad.xlsx.
UNIDADES_POR_TIPO = {
    "temperatura": "°C",
    "presion": "hPa",
    "humedad": "%",
}
 
# Campos que todo registro debe tener.
CAMPOS_OBLIGATORIOS = ["id", "tipo", "valor", "unidad"]
 
 
def campo_esta_vacio(registro, campo):
    """Devuelve True si el campo falta o no tiene contenido.
 
    Se considera vacío si:
      - la clave no existe en el diccionario,
      - vale None,
      - es un texto vacío o solo con espacios ("" o "   ").
    """
    # Si la clave no existe, el campo está vacío (falta).
    if campo not in registro:
        return True
 
    # Guardamos el contenido del campo para revisarlo.
    contenido = registro[campo]
 
    # None significa "no hay dato".
    if contenido is None:
        return True
 
    # Si es texto, quitamos espacios (strip) y vemos si quedó vacío.
    if isinstance(contenido, str) and contenido.strip() == "":
        return True
 
    # Si pasó todas las pruebas anteriores, el campo sí tiene contenido.
    return False
 
 
def es_numero_valido(valor):
    """Devuelve True si 'valor' es un número admitido.
 
    Admitimos:
      - int o float (ejemplo: 295.5),
      - texto que se pueda convertir a número (ejemplo: "295.5").
    No admitimos: "N/D", "ERROR", "?", True/False, nan, inf.
    """
    # En Python True y False cuentan como int (True == 1), pero no son
    # mediciones, así que los rechazamos explícitamente.
    if isinstance(valor, bool):
        return False
 
    # Intentamos convertir a float. Si el texto no es un número
    # (ejemplo "ERROR"), Python lanza ValueError y entramos al except.
    try:
        numero = float(valor)
    except (ValueError, TypeError):
        # ValueError: texto que no es número. TypeError: tipo raro (lista...).
        return False
 
    # float("nan") e float("inf") sí se convierten, pero no son mediciones.
    # Truco: un nan es el único número que NO es igual a sí mismo.
    if numero != numero:
        return False
 
    # Infinito positivo o negativo.
    if numero == float("inf") or numero == float("-inf"):
        return False
 
    # Si llegó hasta aquí, es un número normal.
    return True
 
 
def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str]).
 
    Revisa TODAS las reglas y junta todos los motivos de rechazo
    (no se detiene en el primer error).
    """
    # Lista donde iremos guardando cada problema que encontremos.
    motivos = []
 
    # --- Regla 0: el registro debe ser un diccionario ---
    # Si no lo es, no podemos revisar campos; devolvemos ya.
    if not isinstance(registro, dict):
        return False, ["el registro no es un diccionario"]
 
    # --- A-S10-05: campos obligatorios (id, tipo, valor, unidad) ---
    for campo in CAMPOS_OBLIGATORIOS:
        # Si el campo falta o está vacío, anotamos el motivo.
        if campo_esta_vacio(registro, campo):
            motivos.append("falta el campo obligatorio: " + campo)
 
    # --- A-S10-06: el tipo debe estar permitido ---
    # Solo lo revisamos si el tipo existe; si estaba vacío, ya quedó
    # anotado arriba y no repetimos el problema.
    tipo = registro.get("tipo")
    tipo_es_conocido = False
    if not campo_esta_vacio(registro, "tipo"):
        if tipo in TIPOS_PERMITIDOS:
            tipo_es_conocido = True
        else:
            motivos.append("tipo no permitido: " + str(tipo))
 
    # --- A-S10-07: el valor debe tener formato numérico ---
    # Si el valor estaba vacío, el motivo ya se anotó en la regla de
    # campos obligatorios. Aquí solo revisamos los que sí traen algo.
    if not campo_esta_vacio(registro, "valor"):
        if not es_numero_valido(registro["valor"]):
            motivos.append("el valor no es numérico: " + str(registro["valor"]))
 
    # --- A-S10-08: la unidad debe corresponder al tipo de sensor ---
    # Solo tiene sentido si conocemos el tipo y la unidad existe.
    if tipo_es_conocido and not campo_esta_vacio(registro, "unidad"):
        unidad_esperada = UNIDADES_POR_TIPO[tipo]
        if registro["unidad"] != unidad_esperada:
            motivos.append(
                "unidad incorrecta para " + tipo + ": se esperaba "
                + unidad_esperada + " y llegó " + str(registro["unidad"])
            )
 
    # --- A-S10-09: devolver TODOS los motivos ---
    # Es válido solo si la lista de motivos quedó vacía.
    es_valido = len(motivos) == 0
    return es_valido, motivos
 