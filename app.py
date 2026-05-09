import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ESTÉTICA PROFESIONAL Y CONFIGURACIÓN
st.set_page_config(page_title="VEN-PRO v50.0 - GESTIÓN INTEGRAL", layout="wide")

# CSS personalizado para fondo crema y letras negras (Legibilidad total)
st.markdown("""
    <style>
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; height: 3em !important;
        border: 2px solid #000 !important; background-color: #e8e8e8 !important;
        color: black !important; font-weight: bold; border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] { color: black !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE SEGURIDAD Y ACCESO
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    # Botón de Administrador arriba a la derecha
    col_t, col_adm = st.columns([4, 1])
    with col_adm:
        if st.button("👑 ACCESO ADMIN"): st.toast("Panel de Control Protegido")
    
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login_form"):
            st.subheader("🔑 Inicio de Sesión Segura")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if (u == "ADMIN" and p == "VEN2026") or (u == "CLIENTE1" and p == "12345"):
                    st.session_state.auth = True
                    st.session_state.rol = "ADMINISTRADOR" if u == "ADMIN" else "CLIENTE"
                    st.rerun()
                else: st.error("Acceso denegado. Verifique sus credenciales.")
    st.stop()

# 3. BARRA LATERAL (LUPA DE HISTORIAL Y MENÚ)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    st.info("Consulta movimientos de meses y años anteriores.")
    h_mes = st.selectbox("Mes de consulta:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año de consulta:", [2024, 2025, 2026], index=2)
    st.write("---")
    menu = st.radio("MÓDULOS DEL SISTEMA:", [
        "📊 DASHBOARD", 
        "🛒 LIBROS COMPRAS/VENTAS", 
        "🏛️ ALCALDÍA (GIRARDOT)", 
        "🏢 PARAFISCALES", 
        "📖 LIBRO DIARIO/MAYOR", 
        "📤 SENIAT (XML/TXT)"
    ])
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 4. MÓDULOS CON INFORMACIÓN DETALLADA (FULL DATA)
st.title(f"📂 {menu}")
st.caption(f"Visualizando registros de: {h_mes} {h_anio}")

# LUPA DE BÚSQUEDA GENERAL EN TODOS LOS MÓDULOS
st.text_input(f"🔍 Lupa: Buscar registro específico en {menu} ({h_mes} {h_anio}):", placeholder="Ej: RIF, Nro Factura, Monto...")

if menu == "📊 DASHBOARD":
    st.write("### Resumen Consolidado del Periodo")
    c1, c2, c3 = st.columns(3)
    c1.metric("VENTAS TOTALES", "134.092,96 Bs.")
    c2.metric("COMPRAS TOTALES", "82.410,00 Bs.")
    c3.metric("IVA POR PAGAR", "8.269,27 Bs.")
    st.write("---")
    st.write("#### 📈 Gráfico de Crecimiento Mensual")
    st.line_chart([10, 25, 30, 45, 60])

elif menu == "🛒 LIBROS COMPRAS/VENTAS":
    t1, t2 = st.tabs(["🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS"])
    with t1:
        st.table(pd.DataFrame([{"Fecha": "02/05", "RIF": "J-300123", "Base Imponible": 10000, "IVA": 1600, "Total": 11600}]))
        st.file_uploader("📂 Cargar Documentos de Compras (PDF, EXCEL, FOTO)", key="c", accept_multiple_files=True)
    with t2:
        st.table(pd.DataFrame([{"Fecha": "05/05", "Cliente": "Público General", "Base Imponible": 50000, "IVA": 8000, "Total": 58000}]))
        st.file_uploader("📂 Cargar Documentos de Ventas (PDF, EXCEL, FOTO)", key="v", accept_multiple_files=True)

elif menu == "🏛️ ALCALDÍA (GIRARDOT)":
    st.info("📍 Municipio Girardot - Maracay, Edo. Aragua")
    st.write("### Gestión de Tributos Municipales")
    st.markdown("""
    - **IAE/ISAE:** Ingresos brutos de comercios, industrias o servicios.
    - **Inmuebles Urbanos (Derecho de Frente):** Impuesto sobre propiedad inmobiliaria.
    - **Impuesto sobre Vehículos:** Tasa anual por propiedad de tracción mecánica.
    - **Propaganda y Publicidad Comercial:** Vallas, letreros y publicidad en vehículos.
    - **Espectáculos Públicos y Juegos/Apuestas:** Tasas sobre eventos y azar.
    - **Tasas Administrativas (ASEO y otros):** Aseo urbano, registros o solicitudes.
    """)
    st.selectbox("Seleccione Tributo a consultar/cargar:", ["IAE/ISAE", "Derecho de Frente", "Vehículos", "Publicidad", "Espectáculos", "ASEO/Sateca"])
    st.number_input("Monto del Pago (Bs):", min_value=0.0)
    st.file_uploader("📂 Cargar Solvencia o Comprobante (PDF/Foto)", key="alc")

elif menu == "🏢 PARAFISCALES":
    st.write("### Aportes Patronales y Seguridad Social")
    st.markdown("""
    - **IVSS:** Cobertura de seguridad social para trabajadores y patronos.
    - **FAOV:** Aporte para vivienda gestionado por el BANAVIH.
    - **INCES:** Formación técnica y profesional obligatoria.
    - **Régimen Prestacional de Empleo:** Protección ante pérdida de empleo.
    - **Nueva Ley de Pensiones (2025):** Aporte gestionado por el SENIAT.
    """)
    st.selectbox("Seleccione Ente:", ["IVSS", "FAOV", "INCES", "Régimen de Empleo", "Ley de Pensiones 2025"])
    st.file_uploader("📂 Cargar Soporte de Pago o Planilla (PDF/Foto)", key="para")

elif menu == "📖 LIBRO DIARIO/MAYOR":
    t_diario, t_mayor = st.tabs(["📖 LIBRO DIARIO", "📚 LIBRO MAYOR"])
    with t_diario:
        st.write("### Asientos Contables del Periodo")
        st.table(pd.DataFrame([{"Asiento": 1, "Cuenta": "Caja", "Debe": 1000, "Haber": 0}, {"Asiento": 1, "Cuenta": "Ventas", "Debe": 0, "Haber": 1000}]))
        st.file_uploader("📂 Cargar Folios de Libro Diario (PDF)", key="ld")
    with t_mayor:
        st.write("### Movimientos por Cuenta")
        st.selectbox("Seleccione Cuenta:", ["Banco", "Inventario", "Cuentas por Cobrar", "Capital"])
        st.file_uploader("📂 Cargar Folios de Libro Mayor (PDF)", key="lm")

elif menu == "📤 SENIAT (XML/TXT)":
    st.write("### Generación de Archivos para Portal Fiscal")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("IVA / Retenciones")
        st.button("📦 GENERAR ARCHIVO XML")
        st.file_uploader("Subir archivos TXT de compras/ventas", key="xml_up")
    with col2:
        st.subheader("ISLR")
        st.button("📄 GENERAR ARCHIVO TXT")
        st.file_uploader("Subir planilla de retenciones", key="txt_up")

# PIE DE PÁGINA
st.write("---")
st.caption(f"SISTEMA VEN-PRO - © 2026 Maracay, Aragua. Versión de Alta Seguridad.")
