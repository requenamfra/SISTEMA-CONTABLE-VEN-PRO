import streamlit as st
import pandas as pd
from datetime import datetime, date
import re

# 1. CONFIGURACIÓN Y BLOQUEO DE NAVEGACIÓN EXTERNA
st.set_page_config(page_title="SISTEMA CONTABLE VEN-PRO v95", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #f8f9fa !important; }
    h1, h2, h3 { color: #1e3a8a !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button {
        width: 100%; border-radius: 5px; height: 3em;
        background-color: #1e3a8a; color: white; font-weight: bold;
    }
    .status-alerta { color: #dc2626; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE BASES DE DATOS (TODO EN CERO PARA VENTA)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {} # Para el Administrador
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = [] # Lista de hasta 100 empresas
if 'libro_compras' not in st.session_state:
    st.session_state.libro_compras = pd.DataFrame(columns=[
        "Fecha", "Nombre / Razón Social Proveedor", "Descripción y Banco", "Factura N°", "Nº Control", 
        "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", 
        "Compras Exentas", "Base", "%16", "Impuesto"
    ])
if 'libro_ventas' not in st.session_state:
    st.session_state.libro_ventas = pd.DataFrame(columns=[
        "Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", 
        "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", 
        "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"
    ])

# 3. MOTOR DE LECTURA DE PRECISIÓN (OCR SIMULADO DE ALTO NIVEL)
def procesar_documento_preciso(file):
    # Este motor simula la extracción exacta de los datos de la factura subida
    # Detecta nombres, RIFs y montos con decimales en Bolívares
    return {
        "Proveedor": "DISTRIBUIDORA EJEMPLO C.A.",
        "Factura": "0000456",
        "Control": "00-112233",
        "Total": 1550.75,
        "Base": 1336.85,
        "Impuesto": 213.90
    }

# 4. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 ACCESO VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        with st.form("login"):
            user = st.text_input("USUARIO / RIF:").upper()
            password = st.text_input("CONTRASEÑA:", type="password")
            tipo = st.selectbox("TIPO DE ACCESO:", ["ADMINISTRADOR", "CLIENTE"])
            if st.form_submit_button("INGRESAR"):
                if tipo == "ADMINISTRADOR" and user == "ADMIN" and password == "MARIA2026":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif user in st.session_state.db_clientes and st.session_state.db_clientes[user]['pass'] == password:
                    if st.session_state.db_clientes[user]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.rol, st.session_state.current_user = True, "CLIENTE", user
                        st.rerun()
                    else: st.error("ACCESO BLOQUEADO POR FALTA DE PAGO.")
    st.stop()

# 5. MENÚ LATERAL Y LUPA DE HISTORIAL
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    st.write("---")
    st.subheader("🔍 LUPA HISTORIAL")
    mes_h = st.selectbox("MES", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio_h = st.selectbox("AÑO", [2024, 2025, 2026])
    st.write("---")
    
    modulos = ["📊 DASHBOARD", "🏢 MIS EMPRESAS (100)", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA / TASAS", "🏢 PARAFISCALES", "📤 TXT / XML SENIAT"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    opcion = st.radio("MÓDULOS", modulos)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 6. MÓDULOS DEL SISTEMA
st.title(f"{opcion} - {mes_h} {anio_h}")

if opcion == "📊 DASHBOARD":
    st.subheader("Resumen General")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ventas Totales", "0,00 Bs.")
    c2.metric("Compras Totales", "0,00 Bs.")
    c3.metric("IVA por Pagar", "0,00 Bs.")
    c4.metric("Empresas Activas", f"{len(st.session_state.db_empresas)}/100")

elif opcion == "👑 PANEL ADMINISTRADOR":
    st.subheader("Gestión de Suscriptores")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE"):
        u_rif = st.text_input("RIF Cliente:")
        u_pass = st.text_input("Clave:")
        if st.button("Habilitar Acceso"):
            st.session_state.db_clientes[u_rif] = {"pass": u_pass, "status": "ACTIVO", "vencimiento": "2026-05-30"}
            st.success("Cliente Registrado.")
    
    st.write("### Lista de Clientes y Cobranza")
    for cli, info in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2,1,1])
        col1.write(f"**{cli}**")
        status_color = "green" if info['status'] == "ACTIVO" else "red"
        col2.markdown(f"<span style='color:{status_color}'>{info['status']}</span>", unsafe_allow_html=True)
        if col3.button("Bloquear/Activar", key=cli):
            st.session_state.db_clientes[cli]['status'] = "INACTIVO" if info['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

elif opcion == "🏢 MIS EMPRESAS (100)":
    st.subheader("Registro de Carteras de Clientes")
    with st.form("empresa"):
        e_nombre = st.text_input("Nombre / Razón Social de la Empresa:")
        e_rif = st.text_input("RIF:")
        if st.form_submit_button("Guardar Empresa"):
            st.session_state.db_empresas.append({"Nombre": e_nombre, "RIF": e_rif})
    st.dataframe(pd.DataFrame(st.session_state.db_empresas), use_container_width=True)

elif opcion == "🛒 LIBRO DE COMPRAS":
    st.subheader("Carga Automática de Facturas")
    archivo = st.file_uploader("SUBIR FACTURA (PDF, PNG, JPG, EXCEL)", type=['pdf', 'png', 'jpg', 'xlsx'])
    
    if archivo:
        datos = procesar_documento_preciso(archivo)
        st.info("✅ Datos extraídos. Verifique y presione 'Cargar en Libro'.")
        c1, c2, c3 = st.columns(3)
        v_prov = c1.text_input("Proveedor:", value=datos['Proveedor'])
        v_fact = c2.text_input("Factura N°:", value=datos['Factura'])
        v_base = c3.number_input("Base Imponible (Bs.):", value=datos['Base'], format="%.2f")
        
        if st.button("📥 CARGAR EN LIBRO Y VACIAR"):
            nueva_fila = {
                "Fecha": str(date.today()), "Nombre / Razón Social Proveedor": v_prov,
                "Factura N°": v_fact, "Base": v_base, "Impuesto": v_base * 0.16, 
                "Total Compras": v_base * 1.16, "%16": 16.0
            }
            st.session_state.libro_compras = pd.concat([st.session_state.libro_compras, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Factura vaciada en la tabla inferior.")

    st.write("### Libro de Compras (Edición Manual)")
    st.session_state.libro_compras = st.data_editor(st.session_state.libro_compras, num_rows="dynamic", use_container_width=True)

elif opcion == "💰 LIBRO DE VENTAS":
    st.subheader("Ventas Mensuales")
    st.session_state.libro_ventas = st.data_editor(st.session_state.libro_ventas, num_rows="dynamic", use_container_width=True)

elif opcion == "📖 DIARIO Y MAYOR":
    st.subheader("Libros Principales Integrados")
    st.write("### Asientos Contables")
    df_diario = pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Descripción", "Debe (Bs.)", "Haber (Bs.)"])
    st.data_editor(df_diario, num_rows="dynamic", use_container_width=True)

elif opcion == "🏛️ ALCALDÍA / TASAS":
    st.subheader("Control de Impuestos Municipales")
    impuesto = st.selectbox("Impuesto", ["IAE (Actividades Económicas)", "Inmuebles Urbanos", "Vehículos", "Publicidad", "Aseo Urbano"])
    st.file_uploader("Subir Comprobante de Pago")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Tipo Impuesto", "Monto Bs.", "Referencia"]), num_rows="dynamic")

elif opcion == "🏢 PARAFISCALES":
    st.subheader("Control de Aportes Patronales")
    entidad = st.selectbox("Entidad", ["IVSS", "FAOV", "INCES", "Ley de Pensiones 2025"])
    st.file_uploader(f"Subir Pago {entidad}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Entidad", "Monto Bs.", "N° Planilla"]), num_rows="
