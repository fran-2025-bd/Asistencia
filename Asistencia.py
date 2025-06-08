import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.title("✅ Control de Asistencia - Carmina PA")

# Autenticación con Google
credentials_info = st.secrets["google_service_account"]
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
gc = gspread.authorize(credentials)

# Abrir hoja de cálculo
sh = gc.open("bdcarmina")
worksheet = sh.worksheet("BD")

# Opciones de lista
opciones = [
    "Lista Free",
    "Cumpleaños DANIEL MENDOZA - VIERNES 1 JUN",
    "Cumpleaños FRANCO ONTIVERO - SABADO 2 JUN"
]
lista_seleccionada = st.selectbox("Seleccioná una Lista para marcar asistencia:", opciones)

# Leer datos de la hoja BD
registros = worksheet.get_all_values()[1:]  # Omitimos encabezado
coincidencias = [fila for fila in registros if fila[3] == lista_seleccionada]

if coincidencias:
    st.subheader("Seleccioná quién asistió:")
    asistentes = []

    for i, fila in enumerate(coincidencias):
        nombre_dni = f"{fila[0]} - DNI {fila[1]}"
        if st.checkbox(nombre_dni, key=f"asistencia_{i}"):
            asistentes.append(fila)

    if st.button("Guardar Asistencias"):
        try:
            hoja_asistencias = sh.worksheet("Asistencias")
        except gspread.exceptions.WorksheetNotFound:
            hoja_asistencias = sh.add_worksheet(title="Asistencias", rows="1000", cols="10")
            hoja_asistencias.append_row(["Nombre", "DNI", "Fecha Nacimiento", "Lista", "Estado", "Timestamp"])

        from datetime import datetime
        for persona in asistentes:
            hoja_asistencias.append_row([*persona, "Asistió", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        st.success("✅ Asistencias guardadas correctamente.")
else:
    st.info("No hay registros en esta lista.")
