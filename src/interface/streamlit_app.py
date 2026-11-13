"""Interfaz gráfica docente de DataLab."""
import streamlit as st
import pandas as pd
import plotly.express as px
from src.services.datalab_service import ejecutar_demo, ejecutar_archivo

st.set_page_config(page_title="DataLab | Sensores", page_icon="📊", layout="wide")
st.title("DataLab — Procesamiento y análisis de sensores")
st.caption("Aplicación integradora: calidad, robustez y múltiples fuentes de datos.")

with st.sidebar:
    st.header("Fuente de datos")
    fuente=st.radio("Selecciona el modo", ["Demostración en memoria", "Carga de archivos"])
    archivo=st.file_uploader("Selecciona CSV, JSON o Excel", type=["csv","json","xlsx"]) if fuente == "Carga de archivos" else None

resultado=None
if fuente == "Demostración en memoria":
    resultado=ejecutar_demo()
elif archivo is not None:
    try:
        resultado=ejecutar_archivo(archivo, archivo.name)
    except Exception as exc:
        st.error(f"No fue posible procesar el archivo: {exc}")

if resultado is not None:
    validos=resultado["registros_validos"]
    invalidos=resultado["registros_invalidos"]
    errores=resultado["errores"]
    df=pd.DataFrame(validos)
    resumen=resultado["resumen"]
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Registros recibidos", len(validos)+len(invalidos)+len(errores))
    c2.metric("Válidos", len(validos))
    c3.metric("Inválidos", len(invalidos))
    c4.metric("Errores técnicos", len(errores))
    tab1,tab2,tab3,tab4=st.tabs(["Registros válidos","Indicadores","Calidad","Errores técnicos"])
    with tab1:
        st.subheader("Registros procesados")
        st.dataframe(df, use_container_width=True, hide_index=True)
        if not df.empty:
            st.download_button("Descargar válidos CSV", df.to_csv(index=False).encode("utf-8-sig"), "datalab_validos.csv", "text/csv")
    with tab2:
        st.subheader("Distribución de clasificación")
        if not df.empty:
            conteo=df.groupby(["tipo","clasificacion"]).size().reset_index(name="cantidad")
            st.plotly_chart(px.bar(conteo,x="tipo",y="cantidad",color="clasificacion",barmode="group",text="cantidad"),use_container_width=True)
            st.write(f"Promedio general: **{resumen['promedio']:.2f}**")
        else:
            st.info("No hay registros válidos para calcular indicadores.")
    with tab3:
        if invalidos:
            df_bad=pd.DataFrame([{"id":x["registro"].get("id"),"tipo":x["registro"].get("tipo"),"valor":x["registro"].get("valor"),"motivos":"; ".join(x["motivos"])} for x in invalidos])
            st.dataframe(df_bad,use_container_width=True,hide_index=True)
            st.download_button("Descargar inválidos CSV",df_bad.to_csv(index=False).encode("utf-8-sig"),"datalab_invalidos.csv","text/csv")
        else:
            st.success("No se encontraron registros inválidos.")
    with tab4:
        if errores:
            st.dataframe(
                pd.DataFrame(errores)[["identificador", "categoria", "origen", "mensaje", "fecha_hora"]],
                use_container_width=True, hide_index=True
            )
            st.download_button(
                "Descargar errores técnicos CSV",
                pd.DataFrame(errores).to_csv(index=False).encode("utf-8-sig"),
                "datalab_errores_tecnicos.csv", "text/csv"
            )
        else: st.success("No se registraron errores técnicos.")
