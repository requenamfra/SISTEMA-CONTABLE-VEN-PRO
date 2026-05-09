import streamlit as st
import pandas as pd
from datetime import datetime

# 1. BLOQUEO DE INTERFAZ Y ESTILOS PROFESIONALES
st.set_page_config(page_title="SISTEMA VEN-PRO v70.0", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button { width: 100% !important; border: 2px solid #000 !important; font-weight: bold; }
    .alerta-pago { color: #FF0000 !important; font-weight: bold; animation: blinker 2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS INICIAL (TODO EN CERO PARA VENDER)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = {"DEMO_RIF": {"clave": "1234", "estatus": "Activo", "vence": "2026-05-30"}}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}

# 3. PANTALLA DE ACCESO (LOGIN) BLINDADA
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        with st.form("login"):
            st.subheader("🔐 Ingreso de Usuario")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if u == "ADMIN" and p == "VEN2026":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", u
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ ACCESO BLOQUEADO POR PAGO PENDIENTE.")
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 4. BARRA LATERAL (LUPA Y MENÚ)
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        st.markdown(f"<p class='alerta-pago'>⚠️ MES VENCE: {st.session_state.db_clientes[st.session_state.user]['vence']}</p>", unsafe_allow_html=True)
    
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    modulos = ["📊 DASHBOARD", "🏢 REGISTRO +100 EMPRESAS", "🛒 COMPRAS", "💰 VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES:", modulos)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. DESARROLLO DE MÓDULOS CON VACIADO DE DATOS Y REGISTRO MANUAL
st.title(f"{menu} - {h_mes} {h_anio}")

def tabla_vacia(columnas):
    return st.table(pd.DataFrame(columns=columnas))

# --- PANEL ADMINISTRADOR (COBRANZA) ---
if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Suscriptores")
    for c, data in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2, 2, 1])
        col1.write(f"👤 {c}")
        nuevo_est = col2.selectbox(f"Pago {c}", ["Activo", "Inactivo"], index=0 if data["estatus"]=="Activo" else 1)
        st.session_state.db_clientes[c]["estatus"] = nuevo_est
        if nuevo_est == "Inactivo": col3.error("BLOQUEADO")
        else: col3.success("ACTIVO")

# --- REGISTRO DE EMPRESAS ---
elif menu == "🏢 REGISTRO +100 EMPRESAS":
    st.subheader("Gestión de Cartera (Capacidad 100+)")
    with st.expander("➕ REGISTRAR EMPRESA MANUALMENTE"):
        n = st.text_input("Nombre:")
        r = st.text_input("RIF:")
        if st.button("Guardar Empresa"):
            st.session_state.db_empresas[r] = {"Nombre": n, "Estatus": "Al día"}
            st.success("Empresa Registrada.")
    st.dataframe(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'), use_container_width=True)

# --- COMPRAS / VENTAS CON VACIADO AUTOMÁTICO ---
elif menu in ["🛒 COMPRAS", "💰 VENTAS"]:
    tab1, tab2 = st.tabs(["📤 CARGA INTELIGENTE (IA)", "✍️ REGISTRO MANUAL"])
    with tab1:
        file = st.file_uploader("Subir PDF, Excel o Foto", type=['pdf', 'xlsx', 'png', 'jpg'])
        if file:
            st.success("✅ Archivo leído. Vaciando información...")
            # Simulación de vaciado de datos pedidos
            vaciado = {"Fecha": "08/05/2026", "RIF": "J-312245-0", "Empresa": "PROVEEDOR C.A", "Base Imp.": "100.00", "IVA (16%)": "16.00", "Total Bs.": "116.00"}
            st.json(vaciado)
            if st.button("Confirmar y Guardar en Libro"): st.info("Datos guardados.")
    with tab2:
        with st.form("manual"):
            st.text_input("RIF / Nombre")
            st.number_input("Base Imponible")
            st.form_submit_button("Guardar Registro")
    st.write("### Vista del Libro")
    tabla_vacia(["Fecha", "RIF", "Nombre", "Base Imponible", "IVA", "Total"])

# --- DIARIO Y MAYOR ---
elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Libros Integrados")
    st.file_uploader("Cargar Movimientos", key="dm")
    st.button("✍️ Añadir Asiento Manual")
    st.write("### Libro Diario / Mayor (Datos de Apertura)")
    # Datos de ejemplo para que no esté vacío
    data_diario = {"Fecha": ["01/05/26"], "Cuenta": ["Caja/Banco"], "Debe": ["5000.00"], "Haber": ["0.00"]}
    st.table(pd.DataFrame(data_diario))

# --- PARAFISCALES ---
elif menu == "🏢 PARAFISCALES":
    inst = st.selectbox("Seleccione Institución:", ["IVSS", "FAOV (BANAVIH)", "INCES", "Régimen Empleo", "Ley Pensiones 2025"])
    st.file_uploader(f"Subir pago de {inst}")
    st.button("✍️ Registrar Pago Manualmente")
    tabla_vacia(["Fecha", "Institución", "Nro Referencia", "Monto", "Estatus"])

# --- ALCALDÍA ---
elif menu == "🏛️ ALCALDÍA":
    trib = st.selectbox("Impuesto:", ["IAE/ISAE", "Inmuebles (Derecho Frente)", "Vehículos", "Publicidad", "ASEO/Sateca"])
    st.file_uploader(f"Subir Comprobante {trib}")
    st.button("✍️ Carga Manual de Tasa")
    tabla_vacia(["Fecha", "Impuesto", "Periodo", "Monto Pagado"])

# --- SENIAT ---
elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Control de Archivos Fiscales")
    st.file_uploader("Cargar XML o TXT", accept_multiple_files=True)
    st.button("✍️ Registrar Retención Manual")
    col1, col2 = st.columns(2)
    col1.button("📦 Generar XML IVA")
    col2.button("📄 Generar TXT ISLR")
