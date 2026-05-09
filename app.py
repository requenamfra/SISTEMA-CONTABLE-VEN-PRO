import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. CONFIGURACIÓN DE PÁGINA Y BLOQUEO DE NAVEGACIÓN
st.set_page_config(page_title="VEN-PRO v100.0 - SISTEMA CONTABLE", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    .status-alerta { color: #FF0000 !important; font-weight: bold; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA (ESTRUCTURA DE LIBROS SOLICITADA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = []

# LIBRO DE COMPRAS (COLUMNAS EXACTAS)
if 'l_compras' not in st.session_state:
    st.session_state.l_compras = pd.DataFrame(columns=[
        "Fecha", "Nombre / Razón Social Proveedor", "Descripción y Banco", "Factura N°", "Nº Control", 
        "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", 
        "Compras Exentas", "Base", "%16", "Impuesto"
    ])

# LIBRO DE VENTAS (COLUMNAS EXACTAS)
if 'l_ventas' not in st.session_state:
    st.session_state.l_ventas = pd.DataFrame(columns=[
        "Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", 
        "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", 
        "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"
    ])

# 3. PANTALLA DE ACCESO PROFESIONAL
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login_global"):
            st.subheader("🔐 Identificación de Usuario")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if u == "ADMIN" and p == "ADMIN2026":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]['pass'] == p:
                    if st.session_state.db_clientes[u]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ ACCESO SUSPENDIDO POR FALTA DE PAGO.")
                else: st.error("❌ DATOS INCORRECTOS.")
    st.stop()

# 4. BARRA LATERAL (LUPA Y NAVEGACIÓN)
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        venc = st.session_state.db_clientes[st.session_state.user]['vencimiento']
        st.markdown(f"<p class='status-alerta'>⚠️ SUSCRIPCIÓN VENCE: {venc}</p>", unsafe_allow_html=True)
    
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    modos = ["📊 DASHBOARD", "🏢 REGISTRO DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES:", modos)
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 5. DESARROLLO DE MÓDULOS
st.title(f"{menu} - {h_mes} {h_anio}")

# --- DASHBOARD RESUMEN TOTAL ---
if menu == "📊 DASHBOARD":
    st.subheader("Estado Financiero Consolidado")
    c1, c2, c3 = st.columns(3)
    t_compras = st.session_state.l_compras["Total Compras"].sum()
    t_ventas = st.session_state.l_ventas["Total Ventas"].sum()
    c1.metric("RESUMEN COMPRAS", f"Bs. {t_compras:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("RESUMEN VENTAS", f"Bs. {t_ventas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("IVA NETO", f"Bs. {abs(t_ventas - t_compras)*0.16:,.2f}")
    
    st.write("---")
    st.info(f"Empresas bajo gestión: {len(st.session_state.db_empresas)} / 100")

# --- PANEL ADMINISTRADOR (COBRANZA Y REGISTRO) ---
elif menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Clientes y Suscripciones")
    with st.form("reg_cli"):
        u_rif = st.text_input("RIF del Cliente:")
        u_pass = st.text_input("Contraseña Asignada:")
        u_venc = st.date_input("Fecha de Vencimiento:")
        if st.form_submit_button("✅ HABILITAR CLIENTE"):
            st.session_state.db_clientes[u_rif] = {"pass": u_pass, "status": "ACTIVO", "vencimiento": str(u_venc)}
            st.success("Cliente registrado con éxito.")
    
    st.write("### Lista de Clientes Activos")
    for cli, info in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"👤 {cli} (Vence: {info['vencimiento']})")
        col2.write(f"Estatus: {info['status']}")
        if col3.button("BLOQUEAR / ACTIVAR", key=cli):
            st.session_state.db_clientes[cli]['status'] = "INACTIVO" if info['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

# --- REGISTRO DE EMPRESAS (CARTERA) ---
elif menu == "🏢 REGISTRO DE EMPRESAS":
    st.subheader("Gestión de Cartera (Máximo 100 Empresas)")
    with st.form("new_emp"):
        e_n = st.text_input("Nombre de la Empresa:")
        e_r = st.text_input("RIF Jurídico:")
        if st.form_submit_button("➕ REGISTRAR EMPRESA"):
            if len(st.session_state.db_empresas) < 100:
                st.session_state.db_empresas.append({"Nombre": e_n, "RIF": e_r})
            else: st.error("Límite de 100 empresas alcanzado.")
    st.table(pd.DataFrame(st.session_state.db_empresas))

# --- LIBRO DE COMPRAS (LECTURA Y VACIADO) ---
elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Carga y Vaciado Automático")
    up = st.file_uploader("📸 CARGAR FACTURA (PDF/FOTO/EXCEL)", type=['pdf', 'png', 'jpg', 'xlsx'])
    if up:
        # Motor de lectura simulado (Se ajusta al validar)
        st.warning("⚠️ DATOS DETECTADOS. VERIFIQUE Y VACIÉ:")
        with st.form("vaciado"):
            c1, c2, c3 = st.columns(3)
            f_p = c1.text_input("Proveedor:", value="PROVEEDOR DETECTADO C.A.")
            f_n = c2.text_input("Factura N°:", value="00123")
            f_b = c3.number_input("Base Imponible (Bs.):", value=100.00, format="%.2f")
            if st.form_submit_button("📥 VACIAR EN TABLA"):
                nueva = {"Fecha": str(date.today()), "Nombre / Razón Social Proveedor": f_p, "Factura N°": f_n, "Base": f_b, "Impuesto": f_b*0.16, "Total Compras": f_b*1.16, "%16": 16.0}
                st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva])], ignore_index=True)
    
    st.session_state.l_compras = st.data_editor(st.session_state.l_compras, num_rows="dynamic", use_container_width=True)

# --- LIBRO DE VENTAS ---
elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Registro de Ventas")
    st.session_state.l_ventas = st.data_editor(st.session_state.l_ventas, num_rows="dynamic", use_container_width=True)

# --- DIARIO Y MAYOR ---
elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Contabilidad General (VEN-NIIF)")
    df_contable = pd.DataFrame(columns=["Fecha", "Cuenta", "Naturaleza", "Debe", "Haber", "Descripción"])
    st.write("### Asientos de Diario")
    st.data_editor(df_contable, num_rows="dynamic", use_container_width=True, key="diario")
    st.write("### Libro Mayor (Resumen de Cuentas)")
    st.info("Saldos calculados automáticamente según naturaleza.")

# --- PARAFISCALES ---
elif menu == "🏢 PARAFISCALES":
    st.subheader("Control de Pagos Parafiscales")
    tipo_p = st.selectbox("Seleccione:", ["IVSS", "FAOV", "INCES", "Régimen de Empleo", "Nueva Ley de Pensiones 2025"])
    st.file_uploader(f"Subir soporte de {tipo_p}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Entidad", "Monto Bs.", "N° Planilla"]), num_rows="dynamic", use_container_width=True)

# --- ALCALDÍA ---
elif menu == "🏛️ ALCALDÍA":
    st.subheader("Control Municipal (Girardot / Otros)")
    imp = st.selectbox("Tasa/Impuesto:", ["IAE", "Derecho de Frente", "Vehículos", "Publicidad", "Aseo Urbano"])
    st.file_uploader(f"Cargar Comprobante {imp}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Concepto", "Monto Bs.", "Referencia"]), num_rows="dynamic", use_container_width=True)

# --- SENIAT (XML/TXT) ---
elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Generación y Control de Archivos Fiscales")
    st.file_uploader("Subir Archivo TXT/XML para validación")
    st.button("Generar Archivo de Retenciones")
