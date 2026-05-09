import streamlit as st
import pandas as pd

# 1. SEGURIDAD DE INTERFAZ (BLOQUEO DE MENÚS EXTERNOS)
st.set_page_config(page_title="VEN-PRO v60.0 GLOBAL", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Ocultar botón de Share, GitHub y Menú de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #e8e8e8 !important; color: black !important; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SISTEMA DE GESTIÓN DE DATOS (EMPRESAS Y PAGOS)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'rol' not in st.session_state: st.session_state.rol = None
if 'empresas' not in st.session_state: 
    # Simulación de base de datos para +90 empresas
    st.session_state.empresas = {f"EMPRESA_{i}": {"RIF": f"J-{10000000+i}-0", "Estatus": "Activo"} for i in range(1, 91)}
if 'clientes_pago' not in st.session_state:
    st.session_state.clientes_pago = {"CLIENTE1": "PAGADO", "CLIENTE2": "DEUDOR"}

# 3. PANTALLA DE ACCESO BLINDADA
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login"):
            st.subheader("🔐 Ingreso Protegido")
            user = st.text_input("USUARIO / RIF:").upper()
            password = st.text_input("CONTRASEÑA:", type="password")
            acceso = st.form_submit_button("🔓 ENTRAR")
            
            if acceso:
                if user == "ADMIN" and password == "VEN2026":
                    st.session_state.auth, st.session_state.rol = True, "ADMIN"
                    st.rerun()
                elif user in st.session_state.clientes_pago:
                    if st.session_state.clientes_pago[user] == "PAGADO":
                        st.session_state.auth, st.session_state.rol = True, "CLIENTE"
                        st.rerun()
                    else: st.error("❌ ACCESO BLOQUEADO: Pendiente de Pago Mensual.")
                else: st.error("❌ Credenciales Inválidas.")
    st.stop()

# 4. PANEL LATERAL (LUPA DE HISTORIAL Y CONTROL)
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    opciones = ["📊 DASHBOARD", "🏢 GESTIÓN +90 EMPRESAS", "🛒 LIBROS LEGALES", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": opciones.insert(1, "👑 PANEL DE COBRANZA")
    
    menu = st.radio("MÓDULOS:", opciones)
    if st.button("🔴 CERRAR SISTEMA"):
        st.session_state.auth = False
        st.rerun()

# 5. CONTENIDO DE MÓDULOS FULL DATA
st.title(f"{menu} - {h_mes} {h_anio}")

if menu == "👑 PANEL DE COBRANZA":
    st.subheader("Control de Suscripciones Mensuales")
    for cliente, estado in st.session_state.clientes_pago.items():
        c1, c2, c3 = st.columns([2, 2, 1])
        c1.write(f"👤 {cliente}")
        nuevo_estado = c2.selectbox(f"Estatus {cliente}", ["PAGADO", "DEUDOR"], index=0 if estado=="PAGADO" else 1, key=cliente)
        st.session_state.clientes_pago[cliente] = nuevo_estado
        if nuevo_estado == "DEUDOR": c3.warning("BLOQUEADO")
        else: c3.success("ACTIVO")

elif menu == "🏢 GESTIÓN +90 EMPRESAS":
    st.subheader("Registro Maestro de Cartera")
    with st.expander("➕ REGISTRAR NUEVA EMPRESA"):
        n = st.text_input("Nombre:")
        r = st.text_input("RIF:")
        if st.button("Guardar Empresa"):
            st.session_state.empresas[n] = {"RIF": r, "Estatus": "Activo"}
            st.success("Registrada.")
    
    st.write("### Base de Datos de Clientes")
    df_emp = pd.DataFrame.from_dict(st.session_state.empresas, orient='index')
    st.dataframe(df_emp, use_container_width=True)

elif menu == "🛒 LIBROS LEGALES":
    st.info("Módulo para Libro Diario, Mayor, Compras y Ventas.")
    st.file_uploader("📥 CARGAR DOCUMENTOS (PDF, EXCEL, FOTOS)", accept_multiple_files=True, help="El sistema extraerá la data automáticamente.")
    st.subheader("🔍 Historial de Movimientos")
    st.text_input("Buscar factura o asiento específico:")
    st.table(pd.DataFrame({"Fecha": ["01/05/26"], "Descripción": ["Venta Mercancía"], "Monto": ["15.000 Bs."]}))

elif menu == "🏛️ ALCALDÍA GIRARDOT":
    st.markdown("""
    - **IAE/ISAE:** Ingresos brutos comerciales.
    - **Inmuebles (Derecho de Frente):** Propiedad inmobiliaria.
    - **Vehículos / Publicidad / Espectáculos.**
    - **ASEO (Sateca):** Tasas de servicio.
    """)
    st.file_uploader("Cargar Comprobantes Municipales")

elif menu == "🏢 PARAFISCALES":
    st.markdown("""
    - **IVSS:** Seguro Social.
    - **FAOV:** Vivienda (BANAVIH).
    - **INCES:** Capacitación.
    - **Empleo / Nueva Ley de Pensiones (2025).**
    """)
    st.file_uploader("Cargar Planillas de Pago")

elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Generación de Archivos Fiscales")
    st.button("📦 GENERAR XML RETENCIONES IVA")
    st.button("📄 GENERAR TXT RETENCIONES ISLR")
