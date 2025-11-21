import streamlit as st
import pandas as pd

# ---------- CONFIGURACIÓN ----------
st.set_page_config(layout="wide", page_title="Asignación de Turnos")

df = pd.read_csv("resultado_asignacion.csv")

days = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
shift_names = ["Mañana","Tarde","Noche"]

# Crear tabla legible en formato calendario
calendar_df = pd.DataFrame(columns=["Enfermera", "Día", "Turno"])

for nurse_idx, row in df.iterrows():
    for j, value in enumerate(row):
        if value == 1:
            day = days[j // 3]
            shift = shift_names[j % 3]
            calendar_df.loc[len(calendar_df)] = [f"Enfermera {nurse_idx+1}", day, shift]

# ---------- Título ----------
st.title("📅 Sistema de Asignación Óptima de Turnos")

# ---------- Resumen ----------
st.subheader("📊 Resumen del sistema")

assigned = len(calendar_df)
possible = df.size
coverage = round(assigned / possible * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("Enfermeras", df.shape[0])
col2.metric("Turnos cubiertos", assigned)
col3.metric("Ocupación del sistema", f"{coverage}%")

st.divider()

# ---------- Visualización amigable ----------
st.subheader("👩‍⚕️ Buscar horario de una enfermera")

nurse_selected = st.selectbox("Selecciona una enfermera:", sorted(calendar_df["Enfermera"].unique()))

nurse_schedule = calendar_df[calendar_df["Enfermera"] == nurse_selected]

if nurse_schedule.empty:
    st.warning("Esta enfermera no tiene turnos asignados.")
else:
    st.table(nurse_schedule)

st.divider()

# ---------- Vista por turno ----------
st.subheader("🕒 Buscar quién trabaja un turno específico")

day_choice = st.selectbox("Día:", days)
shift_choice = st.selectbox("Turno:", shift_names)

workers = calendar_df[
    (calendar_df["Día"] == day_choice) &
    (calendar_df["Turno"] == shift_choice)
]["Enfermera"].tolist()

if len(workers) == 0:
    st.info("Nadie cubre este turno.")
else:
    st.success(f"Trabajan: {', '.join(workers)}")

st.divider()

# ---------- Interpretación automática ----------
st.subheader("📌 Interpretación automática")

if coverage < 20:
    st.write("🔍 El sistema asignó pocos turnos debido a reglas estrictas. Es un sistema conservador.")
elif coverage < 60:
    st.write("👍 La distribución es moderada. Respeta descansos y carga balanceada.")
else:
    st.write("⚠️ Alta ocupación. Podría afectar descansos y bienestar laboral.")

st.caption("Modelo basado en programación entera binaria según Yilmaz (2010).")
