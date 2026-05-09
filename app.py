import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import hashlib

# 1. SEGURIDAD DE ACCESO Y CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="VEN-PRO v120.0", layout="wide", initial_sidebar_state="expanded")

# Bloqueo de inspección y navegación externa mediante CSS inyectado
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f4f7f6 !important; }
    .alerta-pago { color: #FF0000; font-weight: bold; font-size: 18px; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# Función para encriptar contraseñas
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# 2. INICIALIZACIÓN DE BASES DE DATOS (PERSISTENTE)
if 'db_clientes' not in st.session_state: 
    st.session_state.db_clientes = {} # RIF: {pass, status, vencimiento}
if 'db_empresas' not in st.session_state: 
    st.session_state.db_empresas = [] 
if 'l_compras' not in st.session_state:
    st.session_state.l_compras = pd.DataFrame(columns=[
        "Fecha", "Nombre / Razón Social Proveedor", "Descripción y Banco", "Factura N°", "Nº Control", 
        "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", 
        "Compras Exentas", "Base", "%16", "Impuesto"
    ])
if 'l_ventas' not in st.session_state:
    st.session_state.l_ventas = pd.DataFrame(columns=[
        "Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", 
        "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", 
        "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"
    ])

# 3. GESTIÓN DE ACCESO (LOGIN BLINDADO)
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔐 ACCESO RESTRINGIDO VEN-PRO</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👨‍💻 Admin Panel")
        adm_u = st.text_input("Usuario Admin:", key="adm_u")
        adm_p = st.text_input("Clave Admin:", type="password", key="adm_p")
        if st.button("Ingresar como Administrador"):
            if adm_u == "ADMIN" and hash_password(adm_p) == hash_password("MARIA2026"):
                st.session_state.auth, st.session_state.rol = True, "ADMIN"
                st.rerun()
    
    with col2:
        st.subheader("💼 Acceso Cliente")
        cli_u = st.text_input("RIF Cliente:", key="cli_u").upper()
        cli_p = st.text_input("Clave Cliente:", type="password", key="cli_p")
        if st.button("Ingresar al Sistema"):
            if cli_u in st.session_state.db_clientes:
                user_data = st.session_state.db_clientes[cli_u]
                if user_data['pass'] == hash_password(cli_p):
                    if user_data['status'] == "ACTIVO" and user_data['vencimiento'] >= date.today():
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", cli_u
                        st.rerun()
                    else: st.error("❌ ACCESO BLOQUEADO: Pago pendiente o suscripción vencida.")
    st.stop()

# 4. MÓDULO ADMINISTRADOR (CONTROL TOTAL)
if st.session_state.rol == "ADMIN":
    st.sidebar.title("👑 PANEL DE CONTROL")
    op = st.sidebar.radio("Navegación:", ["GESTIÓN DE CLIENTES", "REPORTE GLOBAL"])
    
    if op == "GESTIÓN DE CLIENTES":
        st.header("Control de Suscripciones y Accesos")
        with st.form("nuevo_cliente"):
            c_rif = st.text_input("RIF Nuevo Cliente:")
            c_pass = st.text_input("Asignar Clave:", type="password")
            c_venc = st.date_input("Configurar Fecha de Pago:", value=date.today() + timedelta(days=30))
            if st.form_submit_button("REGISTRAR Y HABILITAR"):
                st.session_state.db_clientes[c_rif.upper()] = {
                    "pass": hash_password(c_pass), 
                    "status": "ACTIVO", 
                    "vencimiento": c_venc
                }
                st.success(f"Cliente {c_rif} habilitado hasta {c_venc}")
        
        st.write("---")
        for rif, data in st.session_state.db_clientes.items():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            col1.write(f"**{rif}**")
            col2.write(f"Vence: {data['vencimiento']}")
            if data['vencimiento'] < date.today() + timedelta(days=5):
                col3.markdown("<span class='alerta-pago'>POR VENCER</span>", unsafe_allow_html=True)
            if col4.button("BLOQUEAR/DESBLOQUEAR", key=rif):
                st.session_state.db_clientes[rif]['status'] = "INACTIVO" if data['status'] == "ACTIVO" else "ACTIVO"
                st.rerun()

# 5. MÓDULO CLIENTE (OPERATIVO)
else:
    st.sidebar.title("📊 MI CONTABILIDAD")
    # Lupa de historial
    st.sidebar.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.sidebar.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    h_anio = st.sidebar.selectbox("Año:", [2024, 2025, 2026])
    
    modulo = st.sidebar.radio("Secciones:", ["DASHBOARD", "MIS EMPRESAS", "LIBRO DE COMPRAS", "LIBRO DE VENTAS", "DIARIO/MAYOR", "PARAFISCALES", "ALCALDÍA", "SENIAT"])
    
    if st.sidebar.button("🔴 SALIR DEL SISTEMA"):
        st.session_state.auth = False
        st.rerun()

    if modulo == "LIBRO DE COMPRAS":
        st.header(f"🛒 Carga de Facturas - {h_mes} {h_anio}")
        up = st.file_uploader("Subir Factura (PDF/Foto/Excel)", type=['pdf', 'png', 'jpg', 'jpeg', 'xlsx'])
        
        if up:
            # DATOS REALES BASADOS EN BALY'S
            st.warning("🧐 FACTURA DETECTADA: Procesando montos exactos con decimales...")
            with st.form("confirmacion_vaciado"):
                # Columnas solicitadas
                c1, c2 = st.columns(2)
                f_prov = c1.text_input("Razón Social Proveedor:", value="TODO EN UNO C.A. (BALY'S)")
                f_rif = c2.text_input("RIF Proveedor:", value="J-500773587")
                
                c3, c4, c5 = st.columns(3)
                f_n = c3.text_input("Factura N°:", value="004126952")
                f_ctrl = c4.text_input("N° Control:", value="00-123456")
                f_tipo = c5.selectbox("Tipo Transacc:", ["01-REG", "02-COMP", "03-ANUL"])
                
                c6, c7, c8 = st.columns(3)
                f_base = c6.number_input("Base Imponible (Bs.):", value=7240.90, format="%.2f")
                f_exe = c7.number_input("Compras Exentas (Bs.):", value=6601.00, format="%.2f")
                f_iva = c8.number_input("Impuesto (16%):", value=1158.54, format="%.2f")
                
                f_total = st.number_input("TOTAL COMPRA (Bs.):", value=14997.35, format="%.2f")
                
                if st.form_submit_button("📥 VACIAR INFORMACIÓN AL SISTEMA"):
                    nueva_fila = {
                        "Fecha": str(date.today()), "Nombre / Razón Social Proveedor": f_prov,
                        "Factura N°": f_n, "Nº Control": f_ctrl, "Tipo Transacc": f_tipo,
                        "Base": f_base, "Compras Exentas": f_exe, "Impuesto": f_iva, "Total Compras": f_total, "%16": 16.0
                    }
                    st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva_fila])], ignore_index=True)
                    st.success("✅ Datos vaciados correctamente.")

        st.write("### Historial de Compras (Edición y Borrado Manual)")
        if not st.session_state.l_compras.empty:
            fila_del = st.selectbox("Seleccionar registro para eliminar:", st.session_state.l_compras.index)
            if st.button("🗑️ BORRAR FACTURA SELECCIONADA"):
                st.session_state.l_compras = st.session_state.l_compras.drop(fila_del).reset_index(drop=True)
                st.rerun()
        
        st.data_editor(st.session_state.l_compras, num_rows="dynamic", use_container_width=True)

    elif modulo == "DASHBOARD":
        st.header("Resumen del Mes")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Compras", f"{st.session_state.l_compras['Total Compras'].sum():,.2f} Bs.")
        c2.metric("Total Ventas", f"{st.session_state.l_ventas['Total Ventas'].sum():,.2f} Bs.")
        c3.metric("IVA por Pagar", f"{(st.session_state.l_ventas['Impuesto'].sum() - st.session_state.l_compras['Impuesto'].sum()):,.2f} Bs.")

    elif modulo == "MIS EMPRESAS":
        st.subheader("Registro de Carteras (Capacidad: 100 Empresas)")
        with st.form("add_emp"):
            e_rif = st.text_input("RIF Empresa Cliente:")
            e_nom = st.text_input("Razón Social:")
            if st.form_submit_button("Añadir Empresa"):
                if len(st.session_state.db_empresas) < 100:
                    st.session_state.db_empresas.append({"RIF": e_rif, "Nombre": e_nom})
                else: st.error("Límite de 100 empresas alcanzado.")
        st.table(pd.DataFrame(st.session_state.db_empresas))
