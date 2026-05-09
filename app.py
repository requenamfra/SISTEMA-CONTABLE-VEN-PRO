import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. BLOQUEO TOTAL Y ESTILO PROFESIONAL
st.set_page_config(page_title="VEN-PRO v80.0 GLOBAL", layout="wide")

st.markdown("""
    <style>
    /* Bloqueo de menús de Streamlit y GitHub para el cliente */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label, .stMarkdown { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #e8e8e8 !important; color: black !important; font-weight: bold;
    }
    .status-vencido { color: #FF0000 !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS (ESTRUCTURA VACÍA PARA VENTA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}

# 3. LÓGICA DE VACIADO DE FACTURAS (LECTURA AUTOMÁTICA)
def leer_factura_ia(file):
    # Simulación de motor OCR avanzado para Venezuela
    # En un entorno real, aquí conectamos con un motor de visión
    return {
        "Proveedor": "PROVEEDOR EJEMPLO, C.A.",
        "RIF": "J-12345678-9",
        "Factura": "000125",
        "Control": "00-5544",
        "Base": 1000.50,
        "IVA": 160.08,
        "Total": 1160.58
    }

# 4. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO v80</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login_master"):
            st.subheader("🔐 Acceso al Sistema")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR"):
                if u == "ADMIN" and p == "VEN2026":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", u
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ SUSCRIPCIÓN VENCIDA.")
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 5. PANEL LATERAL (MENÚ Y LUPA)
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user]["vencimiento"], "%Y-%m-%d")
        if (venc - datetime.now()).days <= 5:
            st.markdown(f"<p class='status-vencido'>⚠️ PAGO PENDIENTE: VENCE EL {venc.date()}</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=datetime.now().month-1)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    modulos = ["📊 DASHBOARD", "🏢 GESTIÓN DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("MENÚ:", modulos)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 6. CONTENIDO POR MÓDULOS
st.title(f"{menu} - {h_mes} {h_anio}")

# --- DASHBOARD (RESUMEN GLOBAL) ---
if menu == "📊 DASHBOARD":
    st.subheader("Resumen de Actividad Fiscal")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL VENTAS", "0,00 Bs.")
    c2.metric("TOTAL COMPRAS", "0,00 Bs.")
    c3.metric("IVA POR PAGAR", "0,00 Bs.")
    c4.metric("IMP. MUNICIPAL", "0,00 Bs.")
    st.write("---")
    st.subheader("Estado de Empresas")
    st.info(f"Empresas registradas actualmente: {len(st.session_state.db_empresas)}")

# --- PANEL ADMIN ---
elif menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Suscriptores")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE"):
        c1, c2, c3 = st.columns(3)
        n_u = c1.text_input("Usuario/RIF:")
        n_p = c2.text_input("Clave:")
        n_f = c3.date_input("Vencimiento:")
        if st.button("Habilitar Cliente"):
            st.session_state.db_clientes[n_u] = {"clave": n_p, "estatus": "Activo", "vencimiento": str(n_f)}
            st.success("Habilitado.")
    
    st.write("### Suscriptores Activos")
    if st.session_state.db_clientes:
        for c, d in st.session_state.db_clientes.items():
            col1, col2, col3 = st.columns([2,2,1])
            col1.write(f"👤 {c}")
            col2.write(f"📅 Vence: {d['vencimiento']}")
            if col3.button("BLOQUEAR/ACTIVAR", key=c):
                st.session_state.db_clientes[c]["estatus"] = "Inactivo" if d["estatus"] == "Activo" else "Activo"
                st.rerun()

# --- LIBRO DE COMPRAS (ESTRUCTURA SOLICITADA) ---
elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Vaciado Automático y Registro Manual")
    up = st.file_uploader("📸 Cargar Factura (Foto/PDF/Excel)")
    if up:
        data = leer_factura_ia(up)
        st.success("✅ Factura leída. Verifique los montos abajo.")
        # Aquí se vacía a la tabla manual automáticamente (simulado)
    
    cols_compras = ["Fecha", "Nombre / Razón Social Proveedor", "Factura N°", "Nº Control", "Nota Débito", "Nota Crédito", "Factura Afectada", "Total Compras", "Compras Exentas", "Base Imponible", "%16", "Impuesto IVA"]
    df_c = pd.DataFrame(columns=cols_compras)
    st.data_editor(df_c, num_rows="dynamic", use_container_width=True, key="tabla_compras")

# --- LIBRO DE VENTAS (ESTRUCTURA SOLICITADA) ---
elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Registro de Ventas Nacionales")
    cols_ventas = ["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nombre / Razón Social Cliente", "R.I.F. N°", "Total Ventas", "Ventas Exentas", "Base Imponible", "%16", "Impuesto IVA"]
    df_v = pd.DataFrame(columns=cols_ventas)
    st.data_editor(df_v, num_rows="dynamic", use_container_width=True, key="tabla_ventas")

# --- DIARIO Y MAYOR (CON CUENTAS VEN-NIIF) ---
elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Cuentas VEN-NIIF y Asientos")
    with st.expander("📚 VER PLAN DE CUENTAS (NATURALEZA)"):
        st.write("**DEUDORAS:** Caja, Bancos, Inventarios, Gastos, Costos.")
        st.write("**ACREEDORAS:** Proveedores, IVA Débito, Capital, Ventas.")
    
    st.write("### Asientos Contables")
    df_d = pd.DataFrame(columns=["Fecha", "Código Cuenta", "Descripción Cuenta", "Debe (Bs.)", "Haber (Bs.)"])
    st.data_editor(df_d, num_rows="dynamic", use_container_width=True)

# --- GESTIÓN DE 100 EMPRESAS ---
elif menu == "🏢 GESTIÓN DE EMPRESAS":
    st.subheader("Directorio de Carteras")
    with st.form("emp"):
        n = st.text_input("Nombre / Razón Social:")
        r = st.text_input("RIF Empresa:")
        if st.form_submit_button("Registrar Empresa"):
            st.session_state.db_empresas[r] = {"Nombre": n, "Status": "Al día"}
    st.write(f"Capacidad utilizada: {len(st.session_state.db_empresas)} / 100")
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

# --- ALCALDÍA Y PARAFISCALES ---
elif menu in ["🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES"]:
    st.subheader(f"Control de Pagos y Solvencias: {menu}")
    st.file_uploader("Cargar Comprobante (Foto/PDF)")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Tributo/Institución", "Monto (Bs.)", "Referencia"]), num_rows="dynamic")
