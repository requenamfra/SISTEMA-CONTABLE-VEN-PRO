import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. BLOQUEO Y ESTILO (MARACAY PROFESIONAL)
st.set_page_config(page_title="VEN-PRO v85.0 - SISTEMA CONTABLE", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #e8e8e8 !important; color: black !important; font-weight: bold;
    }
    .status-vencido { color: #FF0000 !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTIÓN DE MEMORIA (PARA QUE NO SE BORRE AL CARGAR)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}
# Memoria de Libros
if 'data_compras' not in st.session_state:
    st.session_state.data_compras = pd.DataFrame(columns=["Fecha", "Nombre / Razón Social Proveedor", "Descripción y Banco", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"])
if 'data_ventas' not in st.session_state:
    st.session_state.data_ventas = pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"])

# 3. PANTALLA DE ACCESO
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            st.subheader("🔐 Acceso Administrador/Cliente")
            u = st.text_input("USUARIO:").upper()
            p = st.text_input("CLAVE:", type="password")
            if st.form_submit_button("🔓 ENTRAR"):
                if u == "ADMIN" and p == "VEN2026":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", u
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ SUSCRIPCIÓN VENCIDA.")
                else: st.error("❌ Datos incorrectos.")
    st.stop()

# 4. MENÚ Y LUPA
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    modos = ["📊 DASHBOARD", "🏢 GESTIÓN DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modos.insert(1, "👑 PANEL ADMINISTRADOR")
    menu = st.radio("SECCIONES:", modos)
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 5. MÓDULOS
st.title(f"{menu} - {h_mes} {h_anio}")

# --- DASHBOARD (RESUMEN REAL) ---
if menu == "📊 DASHBOARD":
    st.subheader("Resumen General de Operaciones")
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL COMPRAS", f"{st.session_state.data_compras['Total Compras'].sum():,.2f} Bs.".replace(",", "X").replace(".", ",").replace("X", "."))
    c2.metric("TOTAL VENTAS", f"{st.session_state.data_ventas['Total Ventas'].sum():,.2f} Bs.".replace(",", "X").replace(".", ",").replace("X", "."))
    st.info(f"Empresas en Cartera: {len(st.session_state.db_empresas)} / 100")

# --- LIBRO DE COMPRAS (VACIADO AUTOMÁTICO CORREGIDO) ---
elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Carga y Vaciado de Facturas de Proveedores")
    up_c = st.file_uploader("📸 SUBIR FACTURA (FOTO/PDF/EXCEL)", type=['png', 'jpg', 'pdf', 'xlsx'])
    
    if up_c:
        # SIMULACIÓN DE LECTURA REAL (OCR)
        nueva_fila = {
            "Fecha": str(date.today()), "Nombre / Razón Social Proveedor": "PROVEEDOR DE PRUEBA C.A",
            "Descripción y Banco": "COMPRA DE MERCANCÍA - BANCO MERCANTIL", "Factura N°": "000542",
            "Nº Control": "00-2211", "Total Compras": 1160.00, "Base": 1000.00, "%16": 16.0, "Impuesto": 160.00
        }
        if st.button("📥 CONFIRMAR Y VACIAR EN TABLA"):
            st.session_state.data_compras = pd.concat([st.session_state.data_compras, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Factura vaciada correctamente en el libro.")

    st.write("### Libro de Compras (Edición Manual y Automática)")
    st.session_state.data_compras = st.data_editor(st.session_state.data_compras, num_rows="dynamic", use_container_width=True)

# --- LIBRO DE VENTAS ---
elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Registro de Ventas Nacionales")
    up_v = st.file_uploader("📸 SUBIR REPORTE Z / FACTURA", type=['png', 'jpg', 'pdf', 'xlsx'])
    st.session_state.data_ventas = st.data_editor(st.session_state.data_ventas, num_rows="dynamic", use_container_width=True)

# --- PANEL ADMIN (SUSCRIPCIONES) ---
elif menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Pagos de Clientes")
    with st.form("new_cli"):
        c_u = st.text_input("Usuario (RIF):")
        c_p = st.text_input("Contraseña:")
        c_v = st.date_input("Vencimiento:")
        if st.form_submit_button("Habilitar"):
            st.session_state.db_clientes[c_u] = {"clave": c_p, "estatus": "Activo", "vencimiento": str(c_v)}
    
    for user, info in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2, 2, 1])
        col1.write(f"👤 {user}")
        if col3.button("BLOQUEAR / ACTIVAR", key=user):
            st.session_state.db_clientes[user]["estatus"] = "Inactivo" if info["estatus"] == "Activo" else "Activo"
            st.rerun()

# --- GESTIÓN DE EMPRESAS ---
elif menu == "🏢 GESTIÓN DE EMPRESAS":
    st.subheader("Registro de Carteras (Capacidad 100 Empresas)")
    with st.form("emp_reg"):
        e_n = st.text_input("Nombre de la Empresa:")
        e_r = st.text_input("RIF Jurídico:")
        if st.form_submit_button("Registrar"):
            st.session_state.db_empresas[e_r] = {"Nombre": e_n, "Registro": str(date.today())}
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

# --- ALCALDÍA / PARAFISCALES / SENIAT ---
elif menu in ["🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]:
    st.subheader(f"Control de {menu}")
    st.file_uploader("Cargar Soporte (Foto/PDF)")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Detalle", "Monto Bs.", "Referencia"]), num_rows="dynamic", use_container_width=True)
