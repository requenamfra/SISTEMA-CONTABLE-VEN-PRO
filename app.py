import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="VEN-PRO v49.0", layout="wide")

# ESTILO VISUAL BLINDADO (NEGRO SOBRE CREMA)
st.markdown("""
    <style>
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; height: 3em !important;
        border: 2px solid #000 !important; background-color: #e8e8e8 !important;
        color: black !important; font-weight: bold; border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE ACCESO SEGURIZADO
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    col_t, col_adm = st.columns([4, 1])
    with col_adm:
        if st.button("👑 ACCESO ADMIN"): st.toast("Panel de Control Administrativo")
    
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if (u == "ADMIN" and p == "VEN2026") or (u == "CLIENTE1" and p == "12345"):
                    st.session_state.auth = True
                    st.session_state.rol = "ADMIN" if u == "ADMIN" else "CLIENTE"
                    st.rerun()
                else: st.error("Acceso Denegado")
    st.stop()

# 3. BARRA LATERAL CON LUPA DE HISTORIAL
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    menu = st.radio("MÓDULOS:", ["📊 DASHBOARD", "🛒 COMPRAS / VENTAS", "🏛️ ALCALDÍA (GIRARDOT)", "🏢 PARAFISCALES", "📖 LIBRO DIARIO/MAYOR", "📤 SENIAT (XML/TXT)"])
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 4. MÓDULOS FULL DATA (MARACAY / ARAGUA)
st.title(f"📂 {menu} - {h_mes} {h_anio}")

if menu == "📊 DASHBOARD":
    c1, c2, c3 = st.columns(3)
    c1.metric("VENTAS TOTALES", "134.092,96 Bs.")
    c2.metric("COMPRAS TOTALES", "82.410,00 Bs.")
    c3.metric("IVA POR PAGAR", "8.269,27 Bs.")
    st.text_input("🔍 Lupa Maestra (Buscar por RIF o Monto):")

elif menu == "🏛️ ALCALDÍA (GIRARDOT)":
    st.info("📍 Municipio Girardot - Maracay, Edo. Aragua")
    st.markdown("""
    **Catálogo de Tributos Girardot:**
    - **IAE/ISAE:** Actividades Económicas (Ingresos Brutos).
    - **Inmuebles Urbanos:** Derecho de Frente.
    - **Vehículos:** Patente de tracción mecánica.
    - **Publicidad:** Propaganda Comercial.
    - **ASEO (Sateca):** Tasas administrativas y de aseo.
    """)
    st.selectbox("Tributo:", ["IAE", "Derecho de Frente", "Vehículos", "Publicidad", "ASEO"])
    st.number_input("Monto pagado (Bs):")
    st.file_uploader("Cargar Comprobante/Solvencia", key="alc")

elif menu == "🏢 PARAFISCALES":
    st.subheader("Aportes Patronales Obligatorios")
    st.markdown("""
    - **IVSS:** Seguro Social.
    - **FAOV:** Política Habitacional (BANAVIH).
    - **INCES:** Capacitación Profesional.
    - **Ley de Pensiones (2025):** Nuevo aporte de protección social.
    """)
    st.selectbox("Institución:", ["IVSS", "FAOV", "INCES", "Pensiones"])
    st.file_uploader("Cargar Soporte de Pago", key="para")

elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Archivos para el Portal Fiscal")
    st.button("📦 GENERAR XML (IVA)")
    st.button("📄 GENERAR TXT (ISLR)")
