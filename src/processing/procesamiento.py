from src.data.lectores import leer_csv, leer_excel, leer_json
from src.exceptions.errores import (
    DataLabError,
    ErrorFormatoFuente,
    ErrorLecturaFuente,
    ErrorValidacion,
    crear_reporte_error,
)
from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro


def procesar_registros(registros):
    """Procesa una lista de registros asegurando que un error individual no detenga el lote."""
    # Validar que la entrada sea una lista o tupla
    if not isinstance(registros, (list, tuple)):
        error = ErrorFormatoFuente("La entrada debe ser una lista de registros")
        reporte = crear_reporte_error("procesamiento_lote", "N/A", str(error), "FORMATO")
        return {
            "registros_validos": [],
            "registros_invalidos": [],
            "errores": [reporte],
            "resumen": {}
        }

    validos = []
    invalidos = []
    errores = []

    for registro in registros:
        # Obtener el ID de forma segura con un diccionario
        id_reg = registro.get("id", "N/A") if isinstance(registro, dict) else "N/A"
        
        try:
            # 1. Normalizar el registro
            registro_norm = normalizar_registro(registro)
            
            # 2. Validar el registro
            es_valido, motivos = validar_registro(registro_norm)
            
            if not es_valido:
                # Si falla la validación, se guardan los motivos
                registro_norm["motivos"] = motivos
                invalidos.append(registro_norm)
            else:
                # 3. Convertir el valor a float y clasificar
                try:
                    valor_num = float(registro_norm["valor"])
                except (ValueError, TypeError):
                    raise ErrorValidacion(f"No se pudo convertir el valor a numérico: {registro_norm.get('valor')}")
                
                registro_norm["valor"] = valor_num
                registro_norm["clasificacion"] = clasificar_valor(valor_num, registro_norm["tipo"])
                validos.append(registro_norm)

        except Exception as error:
            # Capturar el error y asignarle su categoría de forma clara
            if isinstance(error, ErrorValidacion):
                categoria = "VALIDACION"
            elif isinstance(error, ErrorFormatoFuente):
                categoria = "FORMATO"
            elif isinstance(error, ErrorLecturaFuente):
                categoria = "LECTURA"
            else:
                categoria = "DATALAB" if isinstance(error, DataLabError) else "SISTEMA"

            mensaje = str(error) if isinstance(error, DataLabError) else f"Error inesperado: {error}"
            errores.append(crear_reporte_error("procesamiento_lote", id_reg, mensaje, categoria))

    # Retornar el contrato común exigido por el proyecto
    return {
        "registros_validos": validos,
        "registros_invalidos": invalidos,
        "errores": errores,
        "resumen": generar_resumen(validos),
    }


def procesar_archivo(ruta):
    """Lee un archivo externo (CSV, JSON o Excel) y procesa sus registros."""
    ruta_texto = str(ruta)
    
    # Obtener la extensión del archivo de forma sencilla
    extension = ""
    if "." in ruta_texto:
        extension = "." + ruta_texto.rsplit(".", 1)[1].lower()

    # Diccionario para seleccionar el lector adecuado
    lectores = {
        ".csv": leer_csv,
        ".json": leer_json,
        ".xlsx": leer_excel,
    }

    lector = lectores.get(extension)
    if lector is None:
        error = ErrorFormatoFuente(f"Formato no soportado: {extension or 'sin extensión'}")
        reporte = crear_reporte_error(ruta_texto, "N/A", str(error), "FORMATO")
        return {
            "registros_validos": [],
            "registros_invalidos": [],
            "errores": [reporte],
            "resumen": {}
        }

    try:
        registros = lector(ruta)
        return procesar_registros(registros)
    except Exception as error:
        reporte = crear_reporte_error(ruta_texto, "N/A", str(error), "LECTURA")
        return {
            "registros_validos": [],
            "registros_invalidos": [],
            "errores": [reporte],
            "resumen": {}
        }