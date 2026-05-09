import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. SEGURIDAD DE INTERFAZ Y BLOQUEO DE ACCESOS EXTERNOS
st.set_page_config(page_title="VEN-PRO v75.0 - MASTER", layout="wide")
st.markdown("""
    <style>
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

# 2. BASE DE DATOS MAESTRA (TODO EN CERO PARA VENDER)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {} 
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = [] # Para 100+ empresas
if 'libros_data' not in st.session_state: 
    st.session_state.libros_data = {"compras": [], "ventas": []}

# 3. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO v75</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            st.subheader("🔐 Acceso al Sistema")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR"):
                if u == "ADMIN" and p == "ADMIN2026": # Tu acceso
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", u
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ ACCESO BLOQUEADO: Pendiente de Pago Mensual.")
                else: st.error("❌ Datos incorrectos.")
    st.stop()

# 4. BARRA LATERAL (LUPA Y MENÚ)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user]["vencimiento"], "%Y-%m-%d")
        if (venc - datetime.now()).days <= 5:
            st.markdown(f"<p class='status-vencido'>⚠️ ADVERTENCIA: SUSCRIPCIÓN VENCE EL {venc.date()}</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    modulos = ["📊 DASHBOARD", "🏢 REGISTRO DE EMPRESAS (0/100)", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("MENÚ:", modulos)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. FUNCIONES DE VACIADO AUTOMÁTICO (IA)
def vaciar_factura(archivo, tipo):
    # Simula la extracción de los campos exactos que pediste
    return {
        "Nombre / Razón Social Proveedor": "CONTRIBUYENTE DEMO C.A.",
        "DESCRICION Y BANCO": "COMPRA DE MERCANCIA - BANCO MERCANTIL",
        "Factura N°": "000125",
        "Nº Control": "00-9988",
        "Nota de Debito": "0", "Nota de Credito": "0", "Factura Afectada": "N/A",
        "Tipo Transacc": "01-REG",
        "Total Compras": 1160.00, "Compras Exentas": 0.00, "Base": 1000.00, "%16": 160.00, "Impuesto": 160.00
    }

# 6. DESARROLLO DE MÓDULOS
st.title(f"{menu} - {h_mes} {h_anio}")

if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Suscriptores (Venta del Sistema)")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE (SUSCRIPCIÓN)"):
        nc = st.text_input("RIF Cliente:")
        pc = st.text_input("Clave:")
        fv = st.date_input("Vencimiento:", value=date(2026, 5, 30))
        if st.button("Habilitar"):
            st.session_state.db_clientes[nc] = {"clave": pc, "estatus": "Activo", "vencimiento": str(fv)}
            st.success("Cliente Registrado.")
    st.write("### Lista de Clientes Activos")
    st.table(pd.DataFrame.from_dict(st.session_state.db_clientes, orient='index'))

elif menu == "🏢 REGISTRO DE EMPRESAS (0/100)":
    st.subheader("Cartera de Empresas (Hasta 100)")
    with st.form("emp"):
        nom = st.text_input("Nombre de Empresa:")
        rif = st.text_input("RIF:")
        if st.form_submit_button("Guardar"):
            st.session_state.db_empresas.append({"Empresa": nom, "RIF": rif})
    st.table(pd.DataFrame(st.session_state.db_empresas))

elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Vaciado de Facturas de Compra")
    up = st.file_uploader("📥 SUBIR PDF/FOTO FACTURA", type=['pdf', 'png', 'jpg'])
    if up:
        res = vaciar_factura(up, "compra")
        st.success("✅ DATOS EXTRAÍDOS")
        st.session_state.libros_data["compras"].append(res)
    
    st.write("### Libro de Compras (Edición Manual y Automática)")
    cols_compra = ["Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"]
    df_c = pd.DataFrame(st.session_state.libros_data["compras"], columns=cols_compra)
    st.data_editor(df_c, num_rows="dynamic", use_container_width=True)

elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Vaciado de Facturas de Venta")
    upv = st.file_uploader("📥 SUBIR FACTURA DE VENTA", type=['pdf', 'png', 'jpg'])
    st.write("### Libro de Ventas")
    cols_venta = ["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Base", "%", "Impuesto", "Total Ventas"]
    df_v = pd.DataFrame(columns=cols_venta)
    st.data_editor(df_v, num_rows="dynamic", use_container_width=True)

elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Contabilidad General (Diario y Mayor)")
    st.file_uploader("Subir Excel de Banco / Asientos", type=['xlsx'])
    st.data_editor(pd.DataFrame([{"Fecha": "08/05/2026", "Cuenta": "CAJA", "Debe": 1000.50, "Haber": 0.00}], columns=["Fecha", "Cuenta", "Debe", "Haber"]), num_rows="dynamic")

elif menu == "🏛️ ALCALDÍA GIRARDOT":
    st.info("Control de Impuestos Municipales")
    tipo = st.selectbox("Impuesto:", ["IAE/ISAE", "Inmuebles Urbanos", "Vehículos", "Publicidad", "ASEO (Sateca)"])
    st.file_uploader(f"Subir Comprobante de {tipo}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Tributo", "Monto Bs.", "Referencia"]), num_rows="dynamic")

elif menu == "🏢 PARAFISCALES":
    st.info("Control Parafiscal (IVSS, FAOV, INCES, Empleo, Pensiones 2025)")
    inst = st.selectbox("Institución:", ["IVSS", "FAOV", "INCES", "Régimen Empleo", "Ley Pensiones 2025"])
    st.file_uploader(f"Subir Pago de {inst}")
    st.data_editor(pd.DataFrame(columns=["Institución", "Mes Pagado", "Monto Bs.", "Estatus"]), num_rows="dynamic")

elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Generación Fiscal")
    st.file_uploader("Subir Retenciones anteriores")
    st.button("📦 GENERAR XML IVA")
    st.button("📄 GENERAR TXT ISLR")

elif menu == "📊 DASHBOARD":
    st.subheader("Resumen General de Operaciones")
    c1, c2, c3 = st.columns(3)
    c1.metric("TOTAL VENTAS", "0,00 Bs.")
    c2.metric("TOTAL COMPRAS", "0,00 Bs.")
    c3.metric("IVA POR PAGAR", "0,00 Bs.")
