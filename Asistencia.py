import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.title("✅ Control de Asistencia - Carmina PA")

# Autenticación con Google
credentials_info = st.secrets["google_service_account"]
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
gc = gspread.authorize(credentials)

# Abrir hoja de cálculo
sh = gc.open("bdcarmina")
worksheet = sh.worksheet("BD")

# Verificamos si existe la hoja de asistencia
try:
    hoja_asistencias = sh.worksheet("Asistencias")
except gspread.exceptions.WorksheetNotFound:
    hoja_asistencias = sh.add_worksheet(title="Asistencias", rows="1000", cols="10")
    hoja_asistencias.append_row(["Nombre", "DNI", "Fecha Nacimiento", "Lista", "Estado", "Timestamp"])

# Seleccionar lista
opciones = [
    "Lista Free",
    "Cumpleaños DANIEL MENDOZA - VIERNES 1 JUN",
    "Cumpleaños FRANCO ONTIVERO - SABADO 2 JUN"
]
lista_seleccionada = st.selectbox("Seleccioná una Lista para marcar asistencia:", opciones)

# Leer datos
registros = worksheet.get_all_values()[1:]  # Omitimos encabezado
coincidencias = [fila for fila in registros if fila[3] == lista_seleccionada]

# Obtener DNIs que ya registraron asistencia
reg_asistencias = hoja_asistencias.get_all_values()[1:]  # Saltamos encabezado
asistieron_dnis = [fila[1] for fila in reg_asistencias if fila[3] == lista_seleccionada]

asistentes_a_guardar = []

if coincidencias:
    st.subheader("Seleccioná quién asistió:")

    for i, fila in enumerate(coincidencias):
        nombre, dni = fila[0], fila[1]
        nombre_dni = f"{nombre} - DNI {dni}"

        # Ya asistió → Mostrar en rojo (sin checkbox)
        if dni in asistieron_dnis:
            st.markdown(f"<span style='color:red'>{nombre_dni} (ya registrado)</span>", unsafe_allow_html=True)
        else:
            if st.checkbox(nombre_dni, key=f"asistencia_{i}"):
                asistentes_a_guardar.append(fila)

    if st.button("Guardar Asistencias"):
        for persona in asistentes_a_guardar:
            hoja_asistencias.append_row([*persona, "Asistió", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        st.success("✅ Asistencias guardadas correctamente.")
        st.experimental_rerun()  # Vuelve a cargar la página para aplicar colores
else:
    st.info("No hay registros en esta lista.")
