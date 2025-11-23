import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- CONFIGURACIÓN ----------
st.set_page_config(layout="wide", page_title="Asignación de Turnos de Enfermería")

st.title("📅 Sistema de Asignación Óptima de Turnos de Enfermería")

# ---------- Entrada de archivo ----------
uploaded_file = st.file_uploader("📁 Cargar archivo CSV generado en MATLAB", type=["csv"])

if not uploaded_file:
    st.info("📌 Sube el archivo generado por MATLAB para visualizar resultados.")
    st.stop()

df = pd.read_csv(uploaded_file)

days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
shift_names = ["Mañana", "Tarde", "Noche"]

# ---------- Construcción de dataframe interpretable ----------
calendar_df = pd.DataFrame(columns=["Enfermera", "Día", "Turno"])

for nurse_idx, row in df.iterrows():
    for j, value in enumerate(row):
        if value == 1:
            day = days[j // 3]
            shift = shift_names[j % 3]
            calendar_df.loc[len(calendar_df)] = [f"Enfermera {nurse_idx + 1}", day, shift]

# ---------- Resumen general ----------
assigned = len(calendar_df)
possible = df.size
coverage = round(assigned / possible * 100, 2)

col1, col2, col3 = st.columns(3)
col1.metric("👩‍⚕️ Enfermeras", df.shape[0])
col2.metric("📌 Turnos asignados", assigned)
col3.metric("⚙️ Ocupación del sistema", f"{coverage}%")

st.divider()

# ---------- Bloque principal con dos columnas ----------
left, right = st.columns(2)

# ------- IZQUIERDA: Buscar enfermera -------
with left:
    st.subheader("🔍 Buscar horario de una enfermera")
    nurse_selected = st.selectbox(
        "Seleccionar enfermera:", sorted(calendar_df["Enfermera"].unique())
    )
    nurse_schedule = calendar_df[calendar_df["Enfermera"] == nurse_selected]

    st.write("📍 Turnos asignados:")
    st.table(nurse_schedule)

    # Mini Heatmap individual
    schedule_matrix = df.loc[int(nurse_selected.split(" ")[1]) - 1].values.reshape(7, 3)
    fig_heat = px.imshow(
        schedule_matrix,
        labels=dict(x="Turno", y="Día"),
        x=shift_names,
        y=days,
        color_continuous_scale=["white", "blue"],
        title=f"Mapa de turnos para {nurse_selected}"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# ------- DERECHA: Buscar turno -------
with right:
    st.subheader("🕒 Buscar quién cubre un turno")
    day_choice = st.selectbox("Día:", days)
    shift_choice = st.selectbox("Turno:", shift_names)

    workers = calendar_df[
        (calendar_df["Día"] == day_choice) &
        (calendar_df["Turno"] == shift_choice)
    ]["Enfermera"].tolist()

    if len(workers) == 0:
        st.info("⛔ Nadie asignado a este turno.")
    else:
        st.success(f"👥 Trabajan: {', '.join(workers)}")

st.divider()

# ---------- Distribución de carga ----------
st.subheader("📊 Distribución de carga de trabajo")

shifts_per_nurse = df.sum(axis=1)

fig_bar = px.histogram(
    shifts_per_nurse,
    nbins=10,
    title="Cantidad de turnos asignados por enfermera",
    labels={"value": "Turnos asignados", "count": "Número de enfermeras"},
    color_discrete_sequence=["#5A8DEE"]
)
st.plotly_chart(fig_bar, use_container_width=True)
