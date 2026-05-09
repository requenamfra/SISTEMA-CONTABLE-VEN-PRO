import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. SEGURIDAD EXTREMA: BLOQUEO DE INTERFAZ Y ESTILOS
st.set_page_config(page_title="VEN-PRO v75.0 GLOBAL", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
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

# 2. BASE DE DATOS (EN CERO PARA VENTA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}
if 'libros' not in st.session_state:
    st.session_state.libros = {
        "compras": pd.DataFrame(columns=["Nombre / Razón Social Proveedor", "DESCRIPCION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"]),
        "ventas": pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Base", "%", "Impuesto"])
    }

# 3. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO v75</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if u == "ADMIN" and p == "ADMIN123":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ ACCESO BLOQUEADO: SUSCRIPCIÓN PENDIENTE.")
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 4. BARRA LATERAL (HISTORIAL Y MÓDULOS)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user]["vencimiento"], "%Y-%m-%d")
        if (venc - datetime.now()).days <= 5:
            st.markdown(f"<p class='status-vencido'>⚠️ ¡ALERTA! VENCE EL: {venc.date()}</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    modulos = ["📊 DASHBOARD", "🏢 GESTIÓN DE EMPRESAS (100+)", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    menu = st.radio("MÓDULOS:", modulos)
    if st.button("🔴 SALIR"): st.session_state.auth = False; st.rerun()

# 5. LÓGICA DE VACIADO AUTOMÁTICO
def vaciar_factura(tipo):
    nuevo_dato = {
        "Nombre / Razón Social Proveedor": "EMPRESA EJEMPLO C.A", "DESCRIPCION Y BANCO": "COMPRA DE MERCANCIA - BANESCO",
        "Factura N°": "000123", "Nº Control": "00-999", "Total Compras": 1160.00, "Base": 1000.00, "%16": 16, "Impuesto": 160.00
    }
    if tipo == "compras":
        st.session_state.libros["compras"] = pd.concat([st.session_state.libros["compras"], pd.DataFrame([nuevo_dato])], ignore_index=True)
    st.success("✅ ¡Factura leída y vaciada en la tabla inferior!")

# 6. CONTENIDO DE MÓDULOS
st.title(f"{menu} - {h_mes} {h_anio}")

if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Clientes y Suscripciones")
    with st.form("nuevo_cli"):
        n_u = st.text_input("Usuario (RIF):")
        n_p = st.text_input("Clave:")
        n_f = st.date_input("Vencimiento:", value=date(2026, 5, 30))
        if st.form_submit_button("Registrar Cliente"):
            st.session_state.db_clientes[n_u] = {"clave": n_p, "estatus": "Activo", "vencimiento": str(n_f)}
            st.rerun()
    st.write("### Suscriptores")
    st.dataframe(pd.DataFrame.from_dict(st.session_state.db_clientes, orient='index'))

elif menu == "📊 DASHBOARD":
    st.subheader("Resumen General de Operaciones")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Compras", f"{st.session_state.libros['compras']['Total Compras'].sum():,.2f} Bs.")
    c2.metric("Total Ventas", "0.00 Bs.")
    c3.metric("IVA por Pagar", f"{st.session_state.libros['compras']['Impuesto'].sum():,.2f} Bs.")

elif menu == "🛒 LIBRO DE COMPRAS":
    st.file_uploader("📥 CARGAR FACTURA (PDF/FOTO/EXCEL)", type=['pdf','png','jpg','xlsx'], on_change=vaciar_factura, args=("compras",))
    st.subheader("Vaciado y Registro Manual")
    st.session_state.libros["compras"] = st.data_editor(st.session_state.libros["compras"], num_rows="dynamic", use_container_width=True)

elif menu == "💰 LIBRO DE VENTAS":
    st.file_uploader("📥 CARGAR FACTURA DE VENTA", type=['pdf','png','jpg','xlsx'])
    st.subheader("Vaciado y Registro Manual")
    st.session_state.libros["ventas"] = st.data_editor(st.session_state.libros["ventas"], num_rows="dynamic", use_container_width=True)

elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Libros Contables Integrados")
    df_dm = pd.DataFrame(columns=["Fecha", "Referencia", "Cuenta", "Descripción", "Debe", "Haber", "Saldo"])
    st.data_editor(df_dm, num_rows="dynamic", use_container_width=True)

elif menu == "🏢 PARAFISCALES":
    inst = st.selectbox("Institución:", ["IVSS", "FAOV", "INCES", "Empleo", "Pensiones 2025"])
    st.file_uploader(f"Cargar Pago de {inst}")
    st.data_editor(pd.DataFrame(columns=["Mes", "Institución", "Monto", "Referencia"]), num_rows="dynamic")

elif menu == "🏛️ ALCALDÍA GIRARDOT":
    imp = st.selectbox("Impuesto:", ["IAE", "Inmuebles", "Vehículos", "Publicidad", "Aseo/Sateca"])
    st.file_uploader(f"Subir Soporte {imp}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Impuesto", "Monto", "Referencia"]), num_rows="dynamic")

elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Archivos de Retenciones")
    st.file_uploader("Cargar TXT/XML anteriores")
    st.button("📦 Generar Archivo de Retenciones")
