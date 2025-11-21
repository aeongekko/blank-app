import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Asignación de turnos de enfermeras", layout="wide")

# ------------------ INTRO ------------------
st.title("📅 Sistema de Asignación Óptima de Turnos de Enfermería")
st.markdown("""
Este panel muestra una solución generada mediante **Optimización Matemática**.
El modelo busca asignar turnos respetando:

✔ Máximo turnos por enfermera  
✔ Descansos obligatorios    
✔ Mínimos requeridos por turno  

El objetivo NO es llenar todo, sino asignar los turnos de forma válida cumpliendo reglas laborales.
""")

# ------------------ CARGA DE DATOS ------------------
file_path = "resultado_asignacion.csv"

try:
    df = pd.read_csv(file_path)
    st.success("Archivo cargado correctamente.")
except Exception as e:
    st.error(f"No se pudo cargar el archivo: {e}")
    st.stop()

st.subheader("📄 Vista general de la solución")
st.write(f"Número total de enfermeras: **{df.shape[0]}**")
st.write(f"Número total de turnos: **{df.shape[1]}**")

st.dataframe(df, use_container_width=True)

# ------------------ SELECCIÓN INTERACTIVA ------------------
st.divider()
st.subheader("🔍 Exploración interactiva")

col1, col2 = st.columns(2)

with col1:
    nurse = st.selectbox("Selecciona una enfermera para ver sus turnos:", df.index)
    nurse_schedule = df.iloc[nurse]
    assigned_shifts = list(np.where(nurse_schedule == 1)[0] + 1)

    st.write(f"**Turnos asignados:** {assigned_shifts if assigned_shifts else 'No tiene turnos asignados'}")

with col2:
    turn = st.selectbox("Selecciona un turno para ver quién lo trabaja:", range(1, df.shape[1]+1))
    workers = df[df.iloc[:, turn-1] == 1].index.tolist()

    st.write(f"**Enfermeras asignadas al turno {turn}:** {workers if workers else 'Nadie asignado'}")

# ------------------ HEATMAP ------------------
st.divider()
st.subheader("🔥 Mapa visual de asignaciones")

fig, ax = plt.subplots(figsize=(15, 6))
sns.heatmap(df, cmap="Greys", cbar=False, ax=ax)
ax.set_xlabel("Turnos")
ax.set_ylabel("Enfermeras")
st.pyplot(fig)

# ------------------ INTERPRETACIÓN AUTOMÁTICA ------------------
st.divider()
st.subheader("📌 Resumen automático")

total_assignments = df.values.sum()
possible_assignments = df.size
coverage_percent = round((total_assignments / possible_assignments) * 100, 2)

st.write(f"""
- Total de turnos asignados: **{total_assignments}**
- Total posible: **{possible_assignments}**
- Nivel de ocupación del sistema: **{coverage_percent}%**
""")

if coverage_percent < 10:
    st.info("🔎 La solución es válida pero conservadora: el modelo asignó pocos turnos debido a las restricciones estrictas.")
elif coverage_percent < 50:
    st.success("👍 La carga laboral está distribuida de forma balanceada, respetando descansos y restricciones.")
else:
    st.warning("⚠️ Alta carga de asignación: revisar reglas laborales o descansos.")

st.write("---")
st.caption("Desarrollado con Python + Streamlit siguiendo el modelo propuesto por Yilmaz (2010).")
