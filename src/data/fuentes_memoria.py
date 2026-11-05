"""Rol C: adaptador de fuentes en memoria."""
"""from src.data.sensores import obtener_registros

def cargar_desde_memoria():
    # Fuente de datos funcional desde la primera entrega.
    
    
    
    return obtener_registros()"""

"""def preparar_registros_prueba():
    Rol C: escenarios adicionales de entrada para pruebas de semana 10.
    # TODO C-S10-01: construir registros con espacios, mayúsculas y formatos diversos.
    # TODO C-S10-02: construir casos incompletos y tipos no reconocidos.
    # TODO C-S10-03: no alterar los 12 registros base.
    # raise NotImplementedError("Pendiente: implementación del rol C, semana 10")"""


import os
os.chdir(r"C:\repositorio_esteban\proyecto_integrador")   # cambia por tu ruta real

import sys
sys.path.append(os.getcwd())
# Este codigo se añade ya que con el codigo original no encuentra la carpeta src

from src.data.sensores import obtener_registros
 
 
def cargar_desde_memoria():
    """Devuelve los 12 registros base de sensores (fuente funcional desde la semana 10).
 
    Returns:
        list[dict]: lista de registros con claves id, tipo, valor y unidad.
    """
    # obtener_registros() construye una lista NUEVA en cada llamada,
    # por lo que quien reciba el resultado puede modificarlo sin dañar la fuente.
    return obtener_registros()
 
 
def preparar_registros_prueba():
    """Construye escenarios adicionales de entrada para las pruebas de la semana 10.
 
    Cubre tres grupos (un TODO por grupo):
      - C-S10-01: formatos diversos (espacios, mayúsculas, números como texto).
      - C-S10-02: registros incompletos.
      - C-S10-02: tipos de sensor no reconocidos.
    Además (C-S10-03) NO toca los 12 registros base: solo devuelve registros nuevos
    con ids propios (serie 1xx), así que no hay riesgo de alterar los originales.
 
    Returns:
        list[dict]: solo los registros de prueba adicionales (sin los 12 base).
        Para usar base + pruebas:  cargar_desde_memoria() + preparar_registros_prueba()
    """
    # --- C-S10-01: formatos diversos -------------------------------------
    # Son datos válidos en el fondo, pero mal escritos. El rol A debería
    # poder limpiarlos (quitar espacios, pasar a minúsculas, convertir a número).
    formatos_diversos = [
        {"id": " T101 ", "tipo": "  Temperatura ", "valor": 21.5, "unidad": " °C "},
        {"id": "p101", "tipo": "PRESION", "valor": 1013.2, "unidad": "HPA"},
        {"id": "H101", "tipo": "Humedad", "valor": "55.5", "unidad": "%"},   # número como texto
        {"id": "T102", "tipo": "TEMPERATURA", "valor": "  19  ", "unidad": "°c"},
        {"id": "P102", "tipo": " presion", "valor": "1008", "unidad": "hPa "},
    ]
 
    # --- C-S10-02 (parte 1): registros incompletos -----------------------
    # Les falta una clave, o el dato viene vacío / None.
    incompletos = [
        {"id": "T103", "tipo": "temperatura", "unidad": "°C"},              # falta "valor"
        {"id": "P103", "tipo": "presion", "valor": None, "unidad": "hPa"},  # valor None
        {"id": "H102", "tipo": "humedad", "valor": "", "unidad": "%"},      # valor vacío
        {"id": "", "tipo": "temperatura", "valor": 20.0, "unidad": "°C"},   # id vacío
        {"id": "H103", "tipo": "humedad", "valor": 45.0},                   # falta "unidad"
        {"id": "T104", "valor": 23.0, "unidad": "°C"},                      # falta "tipo"
    ]
 
    # --- C-S10-02 (parte 2): tipos no reconocidos ------------------------
    # El sistema solo conoce temperatura, presion y humedad.
    # También se incluye un valor no numérico, que aparece en los datasets reales.
    tipos_no_reconocidos = [
        {"id": "V101", "tipo": "viento", "valor": 12.0, "unidad": "km/h"},
        {"id": "X101", "tipo": "", "valor": 10.0, "unidad": "?"},
        {"id": "X102", "tipo": 123, "valor": 5.0, "unidad": "u"},           # tipo que no es texto
        {"id": "T105", "tipo": "temperatura", "valor": "abc", "unidad": "°C"},  # valor no numérico
    ]
 
    # Se crea una lista nueva uniendo los tres grupos. No se usa ningún
    # registro de sensores.py, así que los 12 base quedan intactos (C-S10-03).
    return formatos_diversos + incompletos + tipos_no_reconocidos


print(cargar_desde_memoria())
print(len(cargar_desde_memoria()))
print(preparar_registros_prueba())
print(len(preparar_registros_prueba()))