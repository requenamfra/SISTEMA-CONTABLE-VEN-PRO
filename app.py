import streamlit as st
import pandas as pd
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTÉTICA PROFESIONAL
st.set_page_config(page_title="VEN-PRO v50.0 - GESTIÓN INTEGRAL", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, span, label, .stMarkdown, .stMetric { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; height: 3em !important;
        border: 2px solid #000 !important; background-color: #e8e8e8 !important;
        color: black !important; font-weight: bold; border-radius: 10px;
    }
    .stTab { font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE ACCESO Y MEMORIA
if 'auth' not in st.session_state: st.session_state.auth = False
if 'empresas' not in st.session_state: st.session_state.empresas = []

if not st.session_state.auth:
    col_t, col_adm = st.columns([4, 1])
    with col_adm:
        if st.button("👑 ACCESO ADMIN"): st.toast("Ingrese credenciales de Administrador")
    
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            st.subheader("🔐 Inicio de Sesión")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            st.caption("Admin: ADMIN / Clave: VEN2026")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if (u == "ADMIN" and p == "VEN2026") or (u == "CLIENTE1" and p == "12345"):
                    st.session_state.auth = True
                    st.session_state.rol = "ADMINISTRADOR" if u == "ADMIN" else "CLIENTE"
                    st.rerun()
                else: st.error("Acceso Inválido")
    st.stop()

# 3. BARRA LATERAL: CONTROL TOTAL Y LUPA DE HISTORIAL
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    st.write("---")
    
    # SELECCIÓN DE EMPRESA (PARA EL CONTADOR)
    st.subheader("🏢 EMPRESA ACTIVA")
    lista_nombres = [e['Nombre'] for e in st.session_state.empresas] if st.session_state.empresas else ["Sin Empresas"]
    empresa_actual = st.selectbox("Trabajando con:", lista_nombres)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Consultar Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Consultar Año:", [2024, 2025, 2026], index=2)
    
    st.write("---")
    menu = st.radio("MÓDULOS DEL SISTEMA:", [
        "🏢 GESTIÓN DE EMPRESAS",
        "📊 DASHBOARD", 
        "🛒 LIBROS COMPRA/VENTA", 
        "🏛️ ALCALDÍA (GIRARDOT)", 
        "🏢 PARAFISCALES", 
        "📖 LIBRO DIARIO/MAYOR", 
        "📤 SENIAT (XML/TXT)"
    ])
    
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 4. EJECUCIÓN DE MÓDULOS (FULL DATA)
st.title(f"📂 {menu}")
st.info(f"Visualizando: **{h_mes} {h_anio}** | Empresa: **{empresa_actual}**")

if menu == "🏢 GESTIÓN DE EMPRESAS":
    st.header("📝 Registro de Clientes / Empresas")
    with st.expander("➕ REGISTRAR NUEVA EMPRESA", expanded=True):
        with st.form("reg_empresa"):
            c1, c2 = st.columns(2)
            n_emp = c1.text_input("Nombre de la Empresa / Razón Social:")
            r_emp = c2.text_input("RIF:")
            t_emp = st.selectbox("Tipo:", ["Contribuyente Especial", "Ordinario", "Formal"])
            if st.form_submit_button("💾 GUARDAR EMPRESA"):
                st.session_state.empresas.append({"Nombre": n_emp, "RIF": r_emp, "Tipo": t_emp})
                st.success(f"Empresa {n_emp} registrada exitosamente.")
                st.rerun()
    
    st.subheader("📋 Empresas Bajo Gestión")
    if st.session_state.empresas:
        st.table(pd.DataFrame(st.session_state.empresas))
    else:
        st.warning("No hay empresas registradas aún.")

elif menu == "📊 DASHBOARD":
    c1, c2, c3 = st.columns(3)
    c1.metric("VENTAS DEL MES", "134.092,96 Bs.")
    c2.metric("COMPRAS DEL MES", "82.410,00 Bs.")
    c3.metric("IVA TOTAL", "8.269,27 Bs.")
    st.write("---")
    st.subheader("🔍 Lupa de Movimientos")
    st.text_input("Buscar registro específico en el historial de esta empresa:")

elif menu == "🛒 LIBROS COMPRA/VENTA":
    t1, t2 = st.tabs(["🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS"])
    with t1:
        st.write("### Carga y Control de Compras")
        st.table(pd.DataFrame([{"Fecha": "02/05", "RIF": "J-300123", "Base": 10000, "IVA": 1600, "Total": 11600}]))
        st.file_uploader("Subir Facturas/Excel/Fotos de Compras", type=['pdf', 'xlsx', 'jpg', 'png'], key="c", accept_multiple_files=True)
    with t2:
        st.write("### Carga y Control de Ventas")
        st.table(pd.DataFrame([{"Fecha": "05/05", "Cliente": "Público", "Base": 50000, "IVA": 8000, "Total": 58000}]))
        st.file_uploader("Subir Reportes Z/Excel/Fotos de Ventas", type=['pdf', 'xlsx', 'jpg', 'png'], key="v", accept_multiple_files=True)

elif menu == "🏛️ ALCALDÍA (GIRARDOT)":
    st.subheader("📍 Tributos Municipales - Girardot (Maracay)")
    st.markdown("""
    * **IAE/ISAE:** Impuesto sobre Actividades Económicas (Ingresos Brutos).
    * **Inmuebles Urbanos:** Derecho de Frente sobre propiedad inmobiliaria.
    * **Vehículos:** Tasa anual por propiedad de tracción mecánica.
    * **Propaganda y Publicidad:** Vallas, letreros y publicidad en vehículos.
    * **Espectáculos Públicos:** Tasas sobre eventos y actividades de azar.
    * **ASEO (Sateca):** Pagos por servicio de aseo y tasas administrativas.
    """)
    tipo_a = st.selectbox("Seleccione Tributo:", ["IAE", "Derecho de Frente", "Vehículos", "Publicidad", "Espectáculos", "ASEO"])
    st.number_input(f"Monto a pagar por {tipo_a} (Bs):")
    st.file_uploader("Cargar Comprobante o Solvencia (PDF/Foto)", type=['pdf', 'jpg', 'png'], key="alc")

elif menu == "🏢 PARAFISCALES":
    st.subheader("🏢 Seguridad Social y Aportes Patronales")
    st.markdown("""
    * **IVSS:** Cobertura de seguridad social para trabajadores y patronos.
    * **FAOV:** Aporte para vivienda gestionado por el BANAVIH.
    * **INCES:** Contribución obligatoria para formación técnica.
    * **Régimen de Empleo:** Protección ante la pérdida de empleo.
    * **Ley de Pensiones (2025):** Nuevo aporte de protección social (SENIAT).
    """)
    tipo_p = st.selectbox("Seleccione Institución:", ["IVSS", "FAOV", "INCES", "Régimen de Empleo", "Ley de Pensiones"])
    st.file_uploader(f"Cargar Planilla o Comprobante de {tipo_p}", type=['pdf', 'jpg', 'png'], key="para")

elif menu == "📖 LIBRO DIARIO/MAYOR":
    st.subheader("📒 Libros Legales Digitalizados")
    st.write("Historial de asientos contables y mayorización.")
    st.text_input("🔍 Lupa: Buscar cuenta o folio:")
    st.table(pd.DataFrame([{"Folio": "001", "Cuenta": "Banco", "Debe": 50000, "Haber": 0}]))
    st.file_uploader("Cargar Folios Escaneados (PDF/Foto)", accept_multiple_files=True, key="lib")

elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("📤 Generación de Archivos Fiscales")
    st.info("Prepare sus archivos para el portal fiscal SENIAT.")
    c1, c2 = st.columns(2)
    with c1:
        st.write("**Módulo XML (Retenciones IVA)**")
        st.button("📦 GENERAR XML")
    with c2:
        st.write("**Módulo TXT (Retenciones ISLR)**")
        st.button("📄 GENERAR TXT")
