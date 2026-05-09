import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. CONFIGURACIÓN Y BLOQUEO DE SEGURIDAD
st.set_page_config(page_title="VEN-PRO v100.0 GLOBAL", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fcfaf7 !important; }
    h1, h2, h3, p, label { color: #1a1a1a !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #f0f0f0 !important; color: black !important; font-weight: bold;
    }
    .status-vencido { color: #D32F2F !important; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE MEMORIA (ESTRUCTURA SOLICITADA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}
if 'lib_compra' not in st.session_state:
    st.session_state.lib_compra = pd.DataFrame(columns=["Nombre / Razón Social Proveedor", "Descripción y Banco", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"])
if 'lib_venta' not in st.session_state:
    st.session_state.lib_venta = pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"])

# 3. PANTALLA DE ACCESO (ADMINISTRADOR Y CLIENTE)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO v100</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            st.subheader("🔐 Iniciar Sesión")
            u = st.text_input("Usuario:").upper()
            p = st.text_input("Contraseña:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if u == "ADMIN" and p == "ADMIN2026":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("⛔ SUSCRIPCIÓN VENCIDA / BLOQUEADA")
                else: st.error("❌ Datos incorrectos")
    st.stop()

# 4. MENÚ LATERAL Y LUPA DE HISTORIAL
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        v = datetime.strptime(st.session_state.db_clientes[st.session_state.user]["vencimiento"], "%Y-%m-%d")
        if (v - datetime.now()).days <= 5:
            st.markdown(f"<p class='status-vencido'>⚠️ ¡ADVERTENCIA! SU MES SE ESTÁ ACABANDO: {v.date()}</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    modulos = ["📊 DASHBOARD", "🏢 GESTIÓN DE EMPRESAS (100)", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    menu = st.radio("MÓDULOS:", modulos)
    
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. CONTENIDO DE MÓDULOS
st.title(f"{menu} - {h_mes} {h_anio}")

# --- DASHBOARD ---
if menu == "📊 DASHBOARD":
    st.subheader("Resumen de Operaciones")
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL COMPRAS", f"{st.session_state.lib_compra['Total Compras'].sum():,.2f} Bs.".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("TOTAL VENTAS", f"{st.session_state.lib_venta['Total Ventas'].sum():,.2f} Bs.".replace(",", "X").replace(".", ",").replace("X", "."))
    c3.metric("EMPRESAS REGISTRADAS", f"{len(st.session_state.db_empresas)} / 100")

# --- LIBRO DE COMPRAS (VACIADO DE PRECISIÓN) ---
elif menu == "🛒 LIBRO DE COMPRAS":
    st.write("### 📸 Cargar Factura (PDF / FOTO / EXCEL)")
    up = st.file_uploader("Subir documento para vaciado automático", type=['png', 'jpg', 'pdf', 'xlsx'])
    
    if up:
        # SIMULACIÓN DE MOTOR DE LECTURA PRECISA
        st.info("Leyendo factura... Verifique los montos antes de confirmar.")
        with st.form("verificar_vaciado"):
            c1, c2, c3 = st.columns(3)
            v_prov = c1.text_input("Razón Social:", value="INVERSIONES EJEMPLO, C.A.")
            v_fac = c2.text_input("Factura N°:", value="001245")
            v_ctrl = c3.text_input("Control N°:", value="00-887766")
            
            c4, c5, c6 = st.columns(3)
            v_base = c4.number_input("Base Imponible (Bs.):", value=1500.25, format="%.2f")
            v_iva = c5.number_input("IVA 16% (Bs.):", value=240.04, format="%.2f")
            v_total = c6.number_input("Total Compras (Bs.):", value=1740.29, format="%.2f")
            
            if st.form_submit_button("📥 CONFIRMAR Y VACIAR AL LIBRO"):
                nueva = {"Nombre / Razón Social Proveedor": v_prov, "Factura N°": v_fac, "Nº Control": v_ctrl, "Base": v_base, "Impuesto": v_iva, "Total Compras": v_total, "Tipo Transacc": "01-REG"}
                st.session_state.lib_compra = pd.concat([st.session_state.lib_compra, pd.DataFrame([nueva])], ignore_index=True)
                st.success("Factura vaciada en la tabla manual.")

    st.write("---")
    st.write("### Carga Manual y Historial")
    st.session_state.lib_compra = st.data_editor(st.session_state.lib_compra, num_rows="dynamic", use_container_width=True)

# --- PANEL ADMIN (CONTROL DE PAGOS) ---
elif menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Gestión de Clientes y Suscripciones")
    with st.form("admin_cli"):
        u_rif = st.text_input("RIF / Usuario del Cliente:")
        u_pass = st.text_input("Contraseña:")
        u_venc = st.date_input("Fecha de Vencimiento:")
        if st.form_submit_button("Registrar y Dar Acceso"):
            st.session_state.db_clientes[u_rif] = {"clave": u_pass, "estatus": "Activo", "vencimiento": str(u_venc)}
    
    st.write("### Clientes Activos (Control Mensual)")
    for c, d in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2, 2, 1])
        col1.write(f"🏢 {c} - Vence: {d['vencimiento']}")
        if col3.button("BLOQUEAR / DESBLOQUEAR", key=c):
            st.session_state.db_clientes[c]["estatus"] = "Inactivo" if d["estatus"] == "Activo" else "Activo"
            st.rerun()

# --- GESTIÓN DE 100 EMPRESAS ---
elif menu == "🏢 GESTIÓN DE EMPRESAS (100)":
    st.subheader("Registro de Carteras Contables")
    with st.form("reg_emp"):
        n_e = st.text_input("Nombre de la Empresa:")
        r_e = st.text_input("RIF de la Empresa:")
        if st.form_submit_button("Guardar en Cartera"):
            st.session_state.db_empresas[r_e] = {"Nombre": n_e, "Fecha": str(date.today())}
    st.write(f"Capacidad: {len(st.session_state.db_empresas)} / 100")
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

# --- ALCALDÍA / PARAFISCALES / SENIAT ---
elif menu in ["🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]:
    st.subheader(f"Módulo de {menu}")
    st.file_uploader("Seleccionar y Subir Pagos (PDF/JPG/Excel/TXT/XML)")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Tipo Pago", "Monto Bs.", "Referencia"]), num_rows="dynamic", use_container_width=True)

# --- DIARIO Y MAYOR (CUENTAS VEN-NIIF) ---
elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Libros de Contabilidad Principal")
    st.write("**Naturaleza de Cuentas VEN-NIIF activada.**")
    df_m = pd.DataFrame(columns=["Fecha", "Código Cuenta", "Descripción", "Debe", "Haber"])
    st.data_editor(df_m, num_rows="dynamic", use_container_width=True)
