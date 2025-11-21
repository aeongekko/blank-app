import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

# ---------- CONFIGURACIÓN ----------
st.set_page_config(layout="wide", page_title="Asignación de Turnos de Enfermería")

st.title("📅 Sistema de Asignación Óptima de Turnos de Enfermería")

# ---------- Entrada de archivo ----------
uploaded_file = st.file_uploader("📁 Cargar archivo CSV generado en MATLAB", type=["csv"])

if not uploaded_file:
    st.info("📌 Sube el archivo generado por MATLAB para visualizar resultados.")
    st.stop()

df = pd.read_csv(uploaded_file)

days = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
shift_names = ["Mañana","Tarde","Noche"]

# ---------- Construcción de dataframe interpretable ----------
calendar_df = pd.DataFrame(columns=["Enfermera", "Día", "Turno"])

for nurse_idx, row in df.iterrows():
    for j, value in enumerate(row):
        if value == 1:
            day = days[j // 3]
            shift = shift_names[j % 3]
            calendar_df.loc[len(calendar_df)] = [f"Enfermera {nurse_idx+1}", day, shift]

# ---------- Resumen general ----------
assigned = len(calendar_df)
possible = df.size
coverage = round(assigned / possible * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("👩‍⚕️ Enfermeras", df.shape[0])
col2.metric("📌 Turnos asignados", assigned)
col3.metric("⚙️ Ocupación del sistema", f"{coverage}%")

st.divider()

# ---------- Sección 1: Visualización por enfermera ----------
st.subheader("🔎 Buscar horario de una enfermera")
nurse_selected = st.selectbox("Seleccionar enfermera:", sorted(calendar_df["Enfermera"].unique()))

nurse_schedule = calendar_df[calendar_df["Enfermera"] == nurse_selected]

st.write("📍 Turnos asignados:")
st.table(nurse_schedule)

# ---------- Mini Heatmap personal ----------
schedule_matrix = df.loc[int(nurse_selected.split(" ")[1]) - 1].values.reshape(7,3)
fig_heat = px.imshow(schedule_matrix,
                     labels=dict(x="Turno", y="Día"),
                     x=shift_names, y=days,
                     color_continuous_scale=["white", "blue"])

st.plotly_chart(fig_heat, use_container_width=True)


st.divider()

# ---------- Sección 2: Gráfico de carga por enfermera ----------
st.subheader("📊 Distribución de carga por enfermera")

shifts_per_nurse = df.sum(axis=1)
fig_bar = px.histogram(shifts_per_nurse, nbins=10,
                       title="Distribución de cantidad de turnos asignados",
                       labels={"value":"Turnos asignados", "count":"Número de enfermeras"})

st.plotly_chart(fig_bar, use_container_width=True)


# ---------- Sección 3: Vista por turno ----------
st.subheader("🕒 Buscar quién trabaja en un turno específico")

col_day, col_shift = st.columns(2)
day_choice = col_day.selectbox("Día:", days)
shift_choice = col_shift.selectbox("Turno:", shift_names)

workers = calendar_df[
    (calendar_df["Día"] == day_choice) &
    (calendar_df["Turno"] == shift_choice)
]["Enfermera"].tolist()

if len(workers) == 0:
    st.info("⛔ Ninguna enfermera asignada para este turno.")
else:
    st.success(f"👥 Trabajan: {', '.join(workers)}")


st.divider()

# ---------- Sección 4: Interpretación automática ----------
st.subheader("📌 Interpretación del modelo")

if coverage < 20:
    st.write("🔍 **Asignación baja**: el modelo es muy estricto o la demanda es baja.")
elif coverage < 60:
    st.write("👍 **Asignación balanceada**: buena proporción entre descanso y cobertura.")
else:
    st.write("⚠️ **Alta carga laboral**: podría causar fatiga o riesgos laborales.")

st.caption("📖 Modelo construido con programación entera binaria basado en Yilmaz (2012).")
