"""Rol C: lectores de archivos. Implementación del estudiante en semana 12.

Contrato de salida para cada lector: list[dict] con claves id, tipo, valor, unidad.
Los lectores no normalizan ni clasifican: entregan datos crudos al servicio.
"""

def leer_csv(archivo):
    # TODO C-S12-01: leer CSV y devolver lista de diccionarios.
    
    lista_diccionarios = []
    with open(archivo, mode="r", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            lista_diccionarios.append(dict(fila))
    return lista_diccionarios
    
    
    raise NotImplementedError("Pendiente: lector CSV, semana 12")
    

import json

def leer_json(archivo):
    # TODO C-S12-02: leer JSON y devolver lista de diccionarios.
    if isinstance(archivo, dict):
        
        contenido_bytes = list(archivo.values())[0]
        contenido_texto = contenido_bytes.decode('utf-8-sig')
        return json.loads(contenido_texto)
    else:
        with open(archivo, mode="r", encoding="utf-8-sig") as f:
            return json.load(f)
    
    
    raise NotImplementedError("Pendiente: lector JSON, semana 12")

import pandas as pd
import io

def leer_excel(archivo):
    # TODO C-S12-03: leer Excel y devolver lista de diccionarios.
    if isinstance(archivo, dict):
    
        nombre_archivo = list(archivo.keys())[0]
        contenido_bytes = archivo[nombre_archivo]
        df = pd.read_excel(io.BytesIO(contenido_bytes))
    else:
        df = pd.read_excel(archivo)
        
    return df.to_dict(orient='records')

    raise NotImplementedError("Pendiente: lector Excel, semana 12")



