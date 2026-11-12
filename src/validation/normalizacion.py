"""Rol A: normalización y estandarización de registros.

SEMANA 10: implementar las funciones marcadas TODO.
Contrato: recibir un diccionario y devolver una COPIA normalizada.
No modificar el registro original.
"""
CAMPOS_A_LIMPIAR = ["id", "tipo", "unidad", "valor"]

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
        copia["tipo"] = copia["tipo"].lower()
        
    # TODO A-S10-04: devolver una copia; no convertir aún el valor a float aquí.
    
    return copia