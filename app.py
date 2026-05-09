import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. SEGURIDAD Y BLOQUEO DE INTERFAZ (OCULTAR SHARE/EDIT)
st.set_page_config(page_title="VEN-PRO v70.0", layout="wide")
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
    .pago-alerta { color: #FF0000 !important; font-weight: bold; animation: blinker 1.5s linear infinite; font-size: 20px; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS (TODO EN CERO PARA VENTA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state:
    # Formato: "RIF/USER": {"clave": "xxx", "estatus": "Activo", "vencimiento": date}
    st.session_state.db_clientes = {"ADMIN": {"clave": "VEN2026", "estatus": "Activo", "vencimiento": date(2099, 12, 31)}}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}

# 3. ACCESO AL SISTEMA
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO GLOBAL</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ACCEDER AL SISTEMA"):
                if u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.user = True, u
                        st.rerun()
                    else: st.error("❌ ACCESO BLOQUEADO POR FALTA DE PAGO.")
                else: st.error("❌ Usuario o Contraseña incorrectos.")
    st.stop()

# 4. LÓGICA DE VENCIMIENTO (ADVERTENCIA EN ROJO)
user_data = st.session_state.db_clientes[st.session_state.user]
dias_restantes = (user_data["vencimiento"] - date.today()).days

# 5. BARRA LATERAL (LUPA DE HISTORIAL)
with st.sidebar:
    st.title(f"👤 {st.session_state.user}")
    if dias_restantes < 5:
        st.markdown(f"<p class='pago-alerta'>⚠️ ¡ALERTA! SU SUSCRIPCIÓN VENCE EN {dias_restantes} DÍAS</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    modulos = ["📊 DASHBOARD", "🏢 MIS EMPRESAS (0/100)", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 LIBRO DIARIO", "📘 LIBRO MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.user == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES:", modulos)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 6. MÓDULOS FULL DATA
st.title(f"{menu} - {h_mes} {h_anio}")

if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Gestión de Clientes y Cobranza")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE"):
        n_c = st.text_input("Usuario/RIF del Cliente:")
        p_c = st.text_input("Clave:")
        f_v = st.date_input("Vencimiento de Pago:")
        if st.button("Habilitar Cliente"):
            st.session_state.db_clientes[n_c] = {"clave": p_c, "estatus": "Activo", "vencimiento": f_v}
            st.success("Cliente Creado.")
    
    st.write("### Lista de Clientes y Control de Bloqueo")
    for c, d in st.session_state.db_clientes.items():
        if c == "ADMIN": continue
        c1, c2, c3 = st.columns([2, 1, 1])
        c1.write(f"**{c}** (Vence: {d['vencimiento']})")
        est = c2.selectbox("Estado", ["Activo", "Inactivo"], key=f"est_{c}", index=0 if d["estatus"]=="Activo" else 1)
        st.session_state.db_clientes[c]["estatus"] = est
        if est == "Inactivo": c3.error("BLOQUEADO")

elif menu == "🏢 MIS EMPRESAS (0/100)":
    st.subheader("Registro de Clientes Contables")
    with st.form("emp"):
        n_e = st.text_input("Nombre de la Empresa:")
        r_e = st.text_input("RIF:")
        if st.form_submit_button("💾 Guardar Empresa"):
            st.session_state.db_empresas[r_e] = {"Nombre": n_e, "Fecha Registro": date.today()}
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

elif menu == "🛒 LIBRO DE COMPRAS":
    st.file_uploader("📥 CARGAR FACTURAS (PDF/EXCEL/FOTO)", type=['pdf', 'xlsx', 'png', 'jpg'])
    st.write("### Registro de Compras")
    df_c = pd.DataFrame(columns=["Fecha", "RIF Proveedor", "Nombre", "Base Imponible", "IVA (16%)", "Total"])
    st.table(df_c) # Estructura lista para vaciar datos

elif menu == "💰 LIBRO DE VENTAS":
    st.file_uploader("📥 CARGAR REPORTES Z / FACTURAS", type=['pdf', 'xlsx', 'png', 'jpg'])
    st.write("### Registro de Ventas")
    df_v = pd.DataFrame(columns=["Fecha", "RIF Cliente", "Nombre", "Base Imponible", "IVA", "IGTF", "Total"])
    st.table(df_v)

elif menu == "📖 LIBRO DIARIO":
    st.write("### Asientos Contables")
    df_d = pd.DataFrame(columns=["Fecha", "Código Cuenta", "Descripción Asiento", "Debe", "Haber"])
    st.table(df_d)

elif menu == "📘 LIBRO MAYOR":
    st.write("### Movimientos por Cuenta")
    df_m = pd.DataFrame(columns=["Código", "Cuenta", "Saldo Anterior", "Debe", "Haber", "Saldo Actual"])
    st.table(df_m)

elif menu == "🏛️ ALCALDÍA GIRARDOT":
    st.selectbox("Seleccione Impuesto:", ["IAE/ISAE (Ingresos Brutos)", "Inmuebles (Derecho Frente)", "Vehículos", "Publicidad", "Aseo Urbano"])
    st.file_uploader("Subir Comprobante Municipal")
    st.table(pd.DataFrame(columns=["Mes", "Tasa Pagada", "Comprobante"]))

elif menu == "🏢 PARAFISCALES":
    inst = st.selectbox("Institución:", ["IVSS", "FAOV", "INCES", "Régimen Empleo", "Nueva Ley Pensiones 2025"])
    st.file_uploader(f"Subir pago de {inst}")
    st.table(pd.DataFrame(columns=["Periodo", "Monto Aporte Patrono", "Monto Aporte Trabajador", "Total"]))

elif menu == "📤 SENIAT (XML/TXT)":
    st.button("📦 Generar XML Retenciones IVA")
    st.button("📄 Generar TXT Retenciones ISLR")
    st.file_uploader("Cargar TXT/XML para validación")
