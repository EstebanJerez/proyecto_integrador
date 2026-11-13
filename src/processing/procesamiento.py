"""Rol B: orquestación del procesamiento con continuidad por registro.

Flujo de cada registro:
    revisar eventos técnicos -> normalizar (A) -> validar (A)
    -> convertir a número -> clasificar (centralizado) -> resumen

REVISIÓN (semanas 10-12):
  1. Los inválidos se guardan como {"registro": ..., "motivos": [...]},
     que es la forma que lee la interfaz docente (pestaña "Calidad").
  2. Se detectan los eventos técnicos de las fuentes (timeout de sensor y
     filas irregulares marcadas por el lector) y se envían a "errores".
  3. La categoría del error sale de error.CATEGORIA (sin if/elif).
  4. procesar_archivo ya no repite la selección de lector: la delega en
     cargar_datos (Rol C). Antes había dos lugares que decidían qué lector
     usar según la extensión (lógica duplicada).
"""
from src.data.carga_datos import cargar_datos
from src.exceptions.errores import (
    DataLabError,
    ErrorConversion,
    ErrorEstructuraRegistro,
    ErrorEventoSensor,
    ErrorFormatoFuente,
    EVENTOS_TECNICOS,
    crear_reporte_error,
)
from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro

ORIGEN_LOTE = "procesamiento_lote"


def _resultado_vacio(reporte):
    """Contrato común cuando el lote completo no se puede procesar."""
    return {
        "registros_validos": [],
        "registros_invalidos": [],
        "errores": [reporte],
        "resumen": generar_resumen([]),
    }


def _revisar_eventos_tecnicos(registro):
    """Lanza la excepción adecuada si el registro trae una marca técnica.

    No es una regla de calidad (eso es del Rol A): es una falla del origen
    de datos que el Rol B debe registrar sin detener el lote.
    """
    if not isinstance(registro, dict):
        raise ErrorEstructuraRegistro(
            f"El registro no es un diccionario: {type(registro).__name__}"
        )

    # Marca que pone un lector (Rol C) cuando una fila viene rota.
    if "_error_tecnico" in registro:
        origen = registro.get("_origen", "desconocido")
        fila = registro.get("_fila", "?")
        raise ErrorEstructuraRegistro(
            f"{registro['_error_tecnico']} (origen {origen}, fila {fila})"
        )

    # Eventos simulados que reporta el sensor (columna observacion_tecnica):
    # SIMULACION_TIMEOUT_SENSOR, SIMULACION_PAQUETE_INCOMPLETO, ...
    evento = registro.get("observacion_tecnica")
    if isinstance(evento, str) and evento.strip().upper().startswith("SIMULACION_"):
        evento = evento.strip().upper()
        clase_error = EVENTOS_TECNICOS.get(evento, ErrorEventoSensor)
        raise clase_error(f"Evento técnico del sensor: {evento}")


def procesar_registros(registros):
    """Procesa una lista de registros asegurando que un error individual no detenga el lote."""
    # Validar que la entrada sea una lista o tupla
    if not isinstance(registros, (list, tuple)):
        error = ErrorFormatoFuente("La entrada debe ser una lista de registros")
        return _resultado_vacio(
            crear_reporte_error(ORIGEN_LOTE, "N/A", error, error.CATEGORIA)
        )

    validos = []
    invalidos = []
    errores = []

    for registro in registros:
        # Obtener el ID de forma segura (el registro podría no ser un dict)
        id_reg = registro.get("id", "N/A") if isinstance(registro, dict) else "N/A"

        try:
            # 0. Eventos técnicos del origen (timeout, fila irregular, no-dict)
            _revisar_eventos_tecnicos(registro)

            # 1. Normalizar el registro (Rol A) -> devuelve una COPIA
            registro_norm = normalizar_registro(registro)

            # 2. Validar el registro (Rol A)
            es_valido, motivos = validar_registro(registro_norm)

            if not es_valido:
                # REVISIÓN: antes se hacía registro_norm["motivos"] = motivos,
                # mezclando datos del sensor con datos de la revisión. La
                # interfaz espera x["registro"] y x["motivos"] por separado.
                invalidos.append({"registro": registro_norm, "motivos": motivos})
                continue

            # 3. Convertir el valor a float y clasificar
            try:
                valor_num = float(registro_norm["valor"])
            except (ValueError, TypeError) as exc:
                # "raise ... from exc" conserva el error original como causa.
                raise ErrorConversion(
                    f"No se pudo convertir el valor a numérico: {registro_norm.get('valor')}"
                ) from exc

            registro_norm["valor"] = valor_num
            registro_norm["clasificacion"] = clasificar_valor(valor_num, registro_norm["tipo"])
            validos.append(registro_norm)

        except DataLabError as error:
            # Errores conocidos: la categoría viene en la propia excepción.
            errores.append(crear_reporte_error(ORIGEN_LOTE, id_reg, error, error.CATEGORIA))
        except Exception as error:  # noqa: BLE001 - red de seguridad del lote
            # Errores inesperados: se registran y el lote CONTINÚA.
            errores.append(crear_reporte_error(
                ORIGEN_LOTE, id_reg, f"Error inesperado: {error}", "SISTEMA"
            ))

    # Retornar el contrato común exigido por el proyecto
    return {
        "registros_validos": validos,
        "registros_invalidos": invalidos,
        "errores": errores,
        "resumen": generar_resumen(validos),
    }


def procesar_archivo(ruta):
    """Lee un archivo externo (CSV, JSON o Excel) y procesa sus registros.

    REVISIÓN: la elección del lector es responsabilidad de cargar_datos
    (Rol C). Aquí solo se controlan los errores de lectura/formato para que
    lleguen al reporte en lugar de romper la aplicación.
    """
    ruta_texto = str(ruta)
    try:
        registros = cargar_datos(ruta, ruta_texto)
    except DataLabError as error:
        return _resultado_vacio(
            crear_reporte_error(ruta_texto, "N/A", error, error.CATEGORIA)
        )
    except Exception as error:  # noqa: BLE001
        return _resultado_vacio(
            crear_reporte_error(ruta_texto, "N/A", f"Error inesperado: {error}", "LECTURA")
        )
    return procesar_registros(registros)
