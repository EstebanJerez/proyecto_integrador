"""Orquestación del procesamiento.

La clasificación permanece centralizada en clasificacion.py.
"""
from src.exceptions.errores import (
    DataLabError,
    ErrorValidacion,
    crear_reporte_error,
)
from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen


def _obtener_id(reg):
    """Devuelve el id del registro, o "N/A" si no se puede obtener."""
    if isinstance(reg, dict):
        return reg.get("id", "N/A")
    return "N/A"


def procesar_registros(registros):
    resultados_validos = []
    errores_detectados = []

    for reg in registros:
        try:
            identificador = str(reg.get("id", "DESCONOCIDO"))
            tipo_dato = str(reg.get("tipo", "general"))
            valor_bruto = reg.get("valor")

            # Validar valores vacíos, nulos o cadenas de error comunes
            if valor_bruto is None or str(valor_bruto).strip() == "" or str(valor_bruto).upper() in ["N/D", "ERROR", "SIN_DATO", "DESCONOCIDO", "NA", "?", "PENDIENTE", "SIN LECTURA"]:
                raise ErrorValidacion(f"Valor no válido o ausente: {valor_bruto}")

            # Intentar conversión a float
            try:
                valor_numerico = float(valor_bruto)
            except (ValueError, TypeError):
                raise ErrorValidacion(f"No se pudo convertir el valor a numérico: {valor_bruto}")

            # Clasificar el valor
            clasificacion = clasificar_valor(valor_numerico, tipo_dato)

            registro_procesado = {
                "id": identificador,
                "tipo": tipo_dato,
                "valor": valor_numerico,
                "unidad": str(reg.get("unidad", "")),
                "clasificacion": clasificacion
            }
            resultados_validos.append(registro_procesado)

        except DataLabError as e:
            reporte = crear_reporte_error(
                origen="procesamiento_lote",
                identificador=_obtener_id(reg),
                mensaje=str(e),
                categoria="VALIDACION"
            )
            errores_detectados.append(reporte)
        except Exception as e:
            reporte = crear_reporte_error(
                origen="procesamiento_lote",
                identificador=_obtener_id(reg),
                mensaje=f"Error inesperado: {str(e)}",
                categoria="SISTEMA"
            )
            errores_detectados.append(reporte)

    # Claves del contrato común (docs/contratos_modulos.md).
    return {
        "registros_validos": resultados_validos,
        "registros_invalidos": [],
        "errores": errores_detectados,
        "resumen": generar_resumen(resultados_validos),
    }