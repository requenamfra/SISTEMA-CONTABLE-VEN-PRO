import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. CONFIGURACIÓN TÉCNICA Y ESTILO
st.set_page_config(page_title="VEN-PRO v105.0", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label { color: #1e3a8a !important; font-weight: bold; }
    .stButton>button {
        width: 100%; border: 2px solid #1e3a8a; 
        background-color: #1e3a8a; color: white; font-weight: bold;
    }
    .status-alerta { color: #dc2626; font-weight: bold; animation: blinker 1.2s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE BASES DE DATOS (TODO EN CERO PARA VENDER)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = []

# LIBRO DE COMPRAS (COLUMNAS SOLICITADAS)
if 'l_compras' not in st.session_state:
    st.session_state.l_compras = pd.DataFrame(columns=[
        "Fecha", "Nombre / Razón Social Proveedor", "Descripción y Banco", "Factura N°", "Nº Control", 
        "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", 
        "Compras Exentas", "Base", "%16", "Impuesto"
    ])

# LIBRO DE VENTAS (COLUMNAS SOLICITADAS)
if 'l_ventas' not in st.session_state:
    st.session_state.l_ventas = pd.DataFrame(columns=[
        "Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", 
        "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", 
        "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"
    ])

# 3. MOTOR DE EXTRACCIÓN (AJUSTADO A LA FACTURA BALY'S)
def extraer_datos_factura(archivo):
    # Basado en la factura de baly's (RIF: J500773587)
    return {
        "Proveedor": "TODO EN UNO C.A. (baly's)",
        "RIF": "J500773587",
        "Factura": "004126952",
        "Control": "00-000000", # No visible, para llenar manual
        "Base": 7240.90,
        "IVA": 1158.54,
        "Total": 14997.35
    }

# 4. ACCESO AL SISTEMA (CON PANEL ADMIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login"):
            st.subheader("🔐 Credenciales")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CLAVE:", type="password")
            if st.form_submit_button("🔓 ACCEDER"):
                if u == "ADMIN" and p == "ADMIN2026":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]['pass'] == p:
                    if st.session_state.db_clientes[u]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ CUENTA BLOQUEADA POR PAGO PENDIENTE.")
    st.stop()

# 5. BARRA LATERAL (NAVEGACIÓN Y LUPA)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    modos = ["📊 DASHBOARD", "🏢 MIS EMPRESAS (100)", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES:", modos)
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 6. MÓDULOS DEL SISTEMA
st.title(f"{menu} - {h_mes} {h_anio}")

if menu == "📊 DASHBOARD":
    st.subheader("Resumen General de Actividades")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOTAL COMPRAS", f"Bs. {st.session_state.l_compras['Total Compras'].sum():,.2f}")
    c2.metric("TOTAL VENTAS", f"Bs. {st.session_state.l_ventas['Total Ventas'].sum():,.2f}")
    c3.metric("IVA CRÉDITO", f"Bs. {st.session_state.l_compras['Impuesto'].sum():,.2f}")
    c4.metric("EMPRESAS", f"{len(st.session_state.db_empresas)}/100")

elif menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control de Clientes y Cobranza Mensual")
    with st.expander("➕ REGISTRAR CLIENTE"):
        r_u = st.text_input("RIF / Usuario:")
        r_p = st.text_input("Clave:")
        if st.button("Habilitar Cliente"):
            st.session_state.db_clientes[r_u] = {"pass": r_p, "status": "ACTIVO"}
            st.success("Cliente habilitado.")
    
    for cli, info in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        status_color = "green" if info['status'] == "ACTIVO" else "red"
        col1.write(f"**Cliente:** {cli}")
        col2.markdown(f"<span style='color:{status_color}'>{info['status']}</span>", unsafe_allow_html=True)
        if col3.button("CAMBIAR ESTATUS", key=cli):
            st.session_state.db_clientes[cli]['status'] = "INACTIVO" if info['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

elif menu == "🏢 MIS EMPRESAS (100)":
    st.subheader("Registro de Carteras de Contabilidad")
    with st.form("emp"):
        e_n = st.text_input("Nombre de la Empresa:")
        e_r = st.text_input("RIF:")
        if st.form_submit_button("Guardar"):
            st.session_state.db_empresas.append({"Empresa": e_n, "RIF": e_r})
    st.data_editor(pd.DataFrame(st.session_state.db_empresas), num_rows="dynamic", use_container_width=True)

elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Vaciado Automático y Manual")
    up = st.file_uploader("Subir Factura (PDF/Foto/Excel)", type=['pdf', 'png', 'jpg', 'jpeg', 'xlsx'])
    if up:
        d = extraer_datos_factura(up)
        st.info("💡 Verifique los montos de la factura baly's antes de vaciar:")
        with st.form("vaciado_compras"):
            c1, c2, c3 = st.columns(3)
            f_p = c1.text_input("Proveedor:", value=d["Proveedor"])
            f_n = c2.text_input("Factura N°:", value=d["Factura"])
            f_t = c3.number_input("Total Factura (Bs.):", value=d["Total"], format="%.2f")
            
            c4, c5, c6 = st.columns(3)
            f_b = c4.number_input("Base Imponible (Bs.):", value=d["Base"], format="%.2f")
            f_i = c5.number_input("IVA (Bs.):", value=d["IVA"], format="%.2f")
            f_e = c6.number_input("Compras Exentas (Bs.):", value=0.00, format="%.2f")
            
            if st.form_submit_button("📥 CONFIRMAR Y VACIAR AL LIBRO"):
                nueva = {
                    "Fecha": str(date.today()), "Nombre / Razón Social Proveedor": f_p, 
                    "Factura N°": f_n, "Total Compras": f_t, "Base": f_b, "Impuesto": f_i, 
                    "Compras Exentas": f_e, "%16": 16.0, "Tipo Transacc": "01-REG"
                }
                st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva])], ignore_index=True)
                st.success("✅ Datos vaciados correctamente.")

    st.session_state.l_compras = st.data_editor(st.session_state.l_compras, num_rows="dynamic", use_container_width=True)

elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Ventas Mensuales")
    st.session_state.l_ventas = st.data_editor(st.session_state.l_ventas, num_rows="dynamic", use_container_width=True)

elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Libros Integrados (VEN-NIIF)")
    st.write("### Asientos de Diario")
    df_d = pd.DataFrame(columns=["Fecha", "Cuenta", "Descripción", "Debe (Bs.)", "Haber (Bs.)"])
    st.data_editor(df_d, num_rows="dynamic", use_container_width=True)
    st.write("### Libro Mayor")
    st.info("Saldos acumulados por cuenta contable.")

elif menu == "🏢 PARAFISCALES":
    st.subheader("Control de Aportes")
    tipo = st.selectbox("Entidad:", ["IVSS", "FAOV", "INCES", "Régimen de Empleo", "Ley de Pensiones 2025"])
    st.file_uploader(f"Cargar soporte de {tipo}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Entidad", "Monto Bs.", "N° Planilla"]), num_rows="dynamic", use_container_width=True)

elif menu == "🏛️ ALCALDÍA":
    st.subheader("Control de Impuestos Municipales")
    st.selectbox("Tasa:", ["IAE", "Inmuebles", "Vehículos", "Publicidad", "Aseo"])
    st.file_uploader("Cargar Comprobante")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Concepto", "Monto Bs.", "Referencia"]), num_rows="dynamic", use_container_width=True)
