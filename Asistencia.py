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

# Obtener o crear hoja de asistencias
try:
    hoja_asistencias = sh.worksheet("Asistencias")
except gspread.exceptions.WorksheetNotFound:
    hoja_asistencias = sh.add_worksheet(title="Asistencias", rows="1000", cols="10")
    hoja_asistencias.append_row(["Nombre", "DNI", "Fecha Nacimiento", "Lista", "Estado", "Timestamp"])

# Selección de lista
opciones = [
    "Lista Free",
    "Cumpleaños DANIEL MENDOZA - VIERNES 1 JUN",
    "Cumpleaños FRANCO ONTIVERO - SABADO 2 JUN"
]
lista_seleccionada = st.selectbox("Seleccioná una Lista para marcar asistencia:", opciones)

# Obtener registros
registros = worksheet.get_all_values()[1:]  # Omitimos encabezado
coincidencias = [fila for fila in registros if fila[3] == lista_seleccionada]

# Obtener asistencias previas
asistencias_previas = hoja_asistencias.get_all_values()[1:]  # Omitimos encabezado
asistieron_dnis = {
    fila[1] for fila in asistencias_previas
    if fila[3] == lista_seleccionada and fila[4].lower() == "asistió"
}

asistentes_a_guardar = []

if coincidencias:
    st.subheader("Seleccioná quién asistió:")

    for i, fila in enumerate(coincidencias):
        nombre, dni = fila[0], fila[1]
        nombre_dni = f"{nombre} - DNI {dni}"

        if dni in asistieron_dnis:
            # Mostrar en rojo si ya asistió
            st.markdown(f"<p style='color:red'>{nombre_dni} (asistencia registrada)</p>", unsafe_allow_html=True)
        else:
            # Mostrar checkbox si aún no asistió
            if st.checkbox(nombre_dni, key=f"check_{i}"):
                asistentes_a_guardar.append(fila)

    if asistentes_a_guardar and st.button("Guardar Asistencias"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for persona in asistentes_a_guardar:
            hoja_asistencias.append_row([*persona, "Asistió", now])
        st.success("✅ Asistencias guardadas correctamente.")
        st.experimental_rerun()  # Refresca la página para actualizar el color rojo
else:
    st.info("No hay registros para esta lista.")
