import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTÉTICA PREMIUM
st.set_page_config(page_title="VEN-PRO v50.0 - SISTEMA INTEGRAL", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; height: 3em !important;
        border: 2px solid #000 !important; background-color: #e8e8e8 !important;
        color: black !important; font-weight: bold; border-radius: 10px;
    }
    .css-1kyx60p { background-color: #eeeeee !important; border-radius: 15px; padding: 20px; border: 1px solid #000; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIÓN DE ESTADO (MEMORIA DEL SISTEMA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'empresas' not in st.session_state: st.session_state.empresas = []

# 3. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login_form"):
            st.subheader("🔐 Control de Acceso")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            st.write("---")
            st.caption("ADMINISTRADOR: Ingrese credenciales maestras.")
            if st.form_submit_button("🔓 ACCEDER AL SISTEMA"):
                if (u == "ADMIN" and p == "VEN2026") or (u == "CLIENTE1" and p == "12345"):
                    st.session_state.auth = True
                    st.session_state.rol = "ADMINISTRADOR" if u == "ADMIN" else "CLIENTE"
                    st.rerun()
                else: st.error("⚠️ Usuario o Clave incorrectos")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL Y MENÚ)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Consultar Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Consultar Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    # Selector de Empresa si hay registradas
    if st.session_state.empresas:
        empresa_actual = st.selectbox("🏢 EMPRESA ACTIVA:", st.session_state.empresas)
    else:
        st.warning("No hay empresas registradas.")
        empresa_actual = "Ninguna"

    st.write("---")
    menu = st.radio("MÓDULOS DEL SISTEMA:", [
        "📊 DASHBOARD", 
        "🏢 REGISTRO DE EMPRESAS",
        "🛒 LIBROS DE COMPRA/VENTA", 
        "📖 DIARIO Y MAYOR",
        "🏛️ ALCALDÍA (GIRARDOT)", 
        "🏢 PARAFISCALES", 
        "📤 GENERAR XML / TXT"
    ])
    
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. DESARROLLO DE MÓDULOS FULL DATA
st.title(f"{menu}")
st.caption(f"Visualizando Historial de: {h_mes} {h_anio} | Empresa: {empresa_actual}")

# --- MÓDULO REGISTRO DE EMPRESAS ---
if menu == "🏢 REGISTRO DE EMPRESAS":
    st.subheader("📝 Inscripción de Nuevas Entidades")
    with st.expander("➕ AGREGAR NUEVA EMPRESA", expanded=True):
        with st.form("reg_empresa"):
            nombre_e = st.text_input("Nombre o Razón Social:")
            rif_e = st.text_input("RIF (Ej: J-12345678-9):")
            tipo_e = st.selectbox("Tipo:", ["Contribuyente Especial", "Ordinario", "Persona Natural"])
            if st.form_submit_button("💾 REGISTRAR"):
                if nombre_e and rif_e:
                    st.session_state.empresas.append(f"{nombre_e} ({rif_e})")
                    st.success(f"Empresa {nombre_e} registrada con éxito.")
                    st.rerun()
    
    st.write("### Listado de Empresas en Cartera")
    st.table(st.session_state.empresas)

# --- MÓDULO DASHBOARD ---
elif menu == "📊 DASHBOARD":
    st.write("### Resumen de Movimientos")
    c1, c2, c3 = st.columns(3)
    c1.metric("VENTAS DEL MES", "134.092,96 Bs.")
    c2.metric("COMPRAS DEL MES", "82.410,00 Bs.")
    c3.metric("IVA TOTAL", "8.269,27 Bs.")
    st.write("---")
    st.subheader("🔍 Lupa Maestra de Movimientos")
    st.text_input("Buscar factura, RIF o monto en el historial:")
    st.info("Mostrando datos archivados de periodos anteriores.")

# --- MÓDULO COMPRAS/VENTAS ---
elif menu == "🛒 LIBROS DE COMPRA/VENTA":
    t1, t2 = st.tabs(["🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS"])
    with t1:
        st.subheader(f"Registro de Compras - {h_mes}")
        st.text_input("🔍 Buscar en historial de compras:")
        st.table(pd.DataFrame([{"Fecha": "02/05", "RIF": "J-300123", "Base": 10000, "IVA": 1600, "Total": 11600}]))
        st.file_uploader("Cargar Facturas/Excel/Fotos de Compras", key="up_c", accept_multiple_files=True)
    with t2:
        st.subheader(f"Registro de Ventas - {h_mes}")
        st.text_input("🔍 Buscar en historial de ventas:")
        st.table(pd.DataFrame([{"Fecha": "05/05", "Cliente": "Público", "Base": 50000, "IVA": 8000, "Total": 58000}]))
        st.file_uploader("Cargar Facturas/Excel/Fotos de Ventas", key="up_v", accept_multiple_files=True)

# --- MÓDULO DIARIO/MAYOR ---
elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Contabilidad General")
    st.text_input("🔍 Lupa: Buscar cuenta contable o asiento:")
    st.write("**Asientos del Mes:**")
    st.table(pd.DataFrame([{"Asiento": "001", "Cuenta": "Caja", "Debe": 5000, "Haber": 0}, {"Asiento": "001", "Cuenta": "Ventas", "Debe": 0, "Haber": 5000}]))
    st.file_uploader("Cargar Libro Diario/Mayor Digitalizado (PDF/Excel)", key="lib")

# --- MÓDULO ALCALDÍA ---
elif menu == "🏛️ ALCALDÍA (GIRARDOT)":
    st.info("📍 Municipio Girardot - Maracay, Edo. Aragua")
    st.markdown("""
    **Información de Tributos Municipales:**
    * **IAE/ISAE:** Impuesto sobre Actividades Económicas. Recae sobre ingresos brutos de comercios e industrias.
    * **Inmuebles Urbanos (Derecho de Frente):** Impuesto sobre la propiedad inmobiliaria.
    * **Vehículos:** Tasa anual por propiedad de tracción mecánica.
    * **Propaganda y Publicidad:** Vallas, letreros y publicidad en vehículos.
    * **Espectáculos Públicos:** Tasas sobre eventos y actividades de azar.
    * **ASEO (Sateca):** Pagos por servicios de aseo urbano y tasas administrativas.
    """)
    st.write("---")
    st.subheader("🔍 Lupa de Tributos Pagados")
    st.selectbox("Filtrar por tipo:", ["IAE", "Derecho de Frente", "Vehículos", "Publicidad", "Espectáculos", "ASEO"])
    st.file_uploader("Cargar Comprobantes de Pago / Solvencias", key="up_alc")

# --- MÓDULO PARAFISCALES ---
elif menu == "🏢 PARAFISCALES":
    st.subheader("Obligaciones Patronales y Seguridad Social")
    st.markdown("""
    * **IVSS:** Cobertura de seguridad social para trabajadores y patronos.
    * **FAOV:** Aporte para garantizar acceso a la vivienda (BANAVIH).
    * **INCES:** Contribución obligatoria para formación técnica profesional.
    * **Régimen de Empleo:** Protección del trabajador ante pérdida de empleo.
    * **Nueva Ley de Pensiones (2025):** Aporte gestionado por el SENIAT para fortalecer pensiones.
    """)
    st.write("---")
    st.subheader("🔍 Lupa Parafiscal")
    st.selectbox("Ver Institución:", ["IVSS", "FAOV", "INCES", "Empleo", "Pensiones"])
    st.file_uploader("Cargar Soportes de Pago (PDF/Foto)", key="up_para")

# --- MÓDULO XML/TXT ---
elif menu == "📤 GENERAR XML / TXT":
    st.subheader("Exportación de Archivos Fiscales (SENIAT)")
    st.write("Generación automática según movimientos cargados.")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Retenciones de IVA**")
        st.button("📦 GENERAR XML")
    with c2:
        st.write("**Retenciones de ISLR**")
        st.button("📄 GENERAR TXT")
    st.file_uploader("Cargar TXT/XML anteriores para consulta", key="up_fiscal")
