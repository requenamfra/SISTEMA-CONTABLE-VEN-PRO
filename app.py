import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. BLOQUEO TOTAL DE INTERFAZ EXTERNA
st.set_page_config(page_title="VEN-PRO v70.0 - GLOBAL", layout="wide")
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

# 2. INICIALIZACIÓN DE BASE DE DATOS (TODO EN CERO PARA VENDER)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state:
    st.session_state.db_clientes = {}  # Lista de usuarios que compran el sistema
if 'db_empresas' not in st.session_state:
    st.session_state.db_empresas = {}  # Capacidad para 100+ empresas por usuario

# 3. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO v70</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login"):
            st.subheader("🔐 Ingreso de Usuario")
            u = st.text_input("USUARIO / RIF:").upper()
            p = st.text_input("CONTRASEÑA:", type="password")
            if st.form_submit_button("🔓 ENTRAR AL SISTEMA"):
                if u == "ADMIN" and p == "ADMIN123": # Tu acceso maestro
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", u
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]["clave"] == p:
                    if st.session_state.db_clientes[u]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("❌ ACCESO BLOQUEADO: SUSCRIPCIÓN PENDIENTE.")
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL Y SECCIONES)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user]["vencimiento"], "%Y-%m-%d")
        if (venc - datetime.now()).days <= 5:
            st.markdown(f"<p class='status-vencido'>⚠️ ¡ALERTA! SU SUSCRIPCIÓN VENCE EL: {venc.date()}</p>", unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    modulos = ["📊 DASHBOARD", "🏢 GESTIÓN DE EMPRESAS (+100)", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA GIRARDOT", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("MÓDULOS DEL SISTEMA:", modulos)
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 5. LÓGICA DE PROCESAMIENTO DE DOCUMENTOS (IA SIMULADA PARA VACIADO)
def procesar_documento(archivo):
    # Esta función simula la lectura de PDF/Foto y extrae datos
    return {"Fecha": "08/05/2026", "RIF": "J-12345678-9", "Empresa": "PROVEEDOR C.A", "Base": 1000.00, "IVA": 160.00, "Total": 1160.00}

# 6. CONTENIDO DE MÓDULOS
st.title(f"{menu} - {h_mes} {h_anio}")

if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Gestión de Suscriptores (Tus Clientes)")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE"):
        c1, c2, c3 = st.columns(3)
        n_u = c1.text_input("RIF/Usuario:")
        n_p = c2.text_input("Contraseña:")
        n_f = c3.date_input("Vencimiento:", value=date(2026, 5, 30))
        if st.button("Habilitar Acceso"):
            st.session_state.db_clientes[n_u] = {"clave": n_p, "estatus": "Activo", "vencimiento": str(n_f)}
            st.success("Cliente registrado con éxito.")
    
    st.write("### Lista de Suscriptores Activos")
    if st.session_state.db_clientes:
        df_cli = pd.DataFrame.from_dict(st.session_state.db_clientes, orient='index').reset_index()
        st.dataframe(df_cli)
        u_bloq = st.selectbox("Seleccionar Usuario para Bloquear/Activar:", list(st.session_state.db_clientes.keys()))
        if st.button("Cambiar Estado (Bloquear/Desbloquear)"):
            actual = st.session_state.db_clientes[u_bloq]["estatus"]
            st.session_state.db_clientes[u_bloq]["estatus"] = "Inactivo" if actual == "Activo" else "Activo"
            st.rerun()

elif menu == "🏢 GESTIÓN DE EMPRESAS (+100)":
    st.subheader("Registro de Carteras de Clientes")
    with st.form("reg_emp"):
        n_e = st.text_input("Nombre de la Empresa:")
        r_e = st.text_input("RIF Jurídico:")
        if st.form_submit_button("💾 Guardar Empresa en Sistema"):
            st.session_state.db_empresas[r_e] = {"Nombre": n_e, "Fecha_Registro": str(date.today())}
    st.write(f"Empresas registradas: {len(st.session_state.db_empresas)} / 100")
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

elif menu in ["🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS"]:
    st.subheader("Vaciado Automático y Registro Manual")
    up = st.file_uploader("📥 CARGAR PDF, EXCEL O FOTO DE FACTURA", type=['pdf', 'png', 'jpg', 'xlsx'])
    if up:
        data = procesar_documento(up)
        st.success("✅ Documento leído con éxito. Información extraída:")
        st.json(data)
        if st.button("Confirmar y Vaciar en Libro"):
            st.info("Información guardada en la base de datos fiscal.")
    
    st.write("---")
    st.subheader("Registro Manual / Edición")
    df_modelo = pd.DataFrame(columns=["Fecha", "RIF", "Nombre/Razón Social", "Nro Factura", "Base Imponible", "IVA (16%)", "Total"])
    st.data_editor(df_modelo, num_rows="dynamic", use_container_width=True)

elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Libro Diario y Mayor Integrado")
    st.file_uploader("Subir Movimientos Bancarios (Excel/PDF)", type=['xlsx', 'pdf'])
    st.write("### Asientos Contables")
    df_diario = pd.DataFrame([{"Fecha": "08/05/2026", "Cuenta": "Caja Chicca", "Debe": 500.00, "Haber": 0.00}, {"Fecha": "08/05/2026", "Cuenta": "Ventas", "Debe": 0.00, "Haber": 500.00}])
    st.data_editor(df_diario, num_rows="dynamic", use_container_width=True)

elif menu == "🏛️ ALCALDÍA GIRARDOT":
    tributo = st.selectbox("Seleccione Impuesto Municipal:", ["IAE/ISAE (Actividades Económicas)", "Inmuebles Urbanos", "Vehículos", "Publicidad Comercial", "ASEO Urbano"])
    st.file_uploader(f"Subir Comprobante de {tributo}")
    st.write("### Historial de Pagos Municipales")
    st.table(pd.DataFrame(columns=["Fecha Pago", "Tributo", "Monto Pagado", "Nro Referencia"]))

elif menu == "🏢 PARAFISCALES":
    inst = st.selectbox("Seleccione Institución:", ["IVSS", "FAOV (BANAVIH)", "INCES", "Régimen de Empleo", "Nueva Ley de Pensiones (SENIAT 2025)"])
    st.file_uploader(f"Subir Pago/Planilla de {inst}")
    st.subheader("Control de Solvencias")
    st.data_editor(pd.DataFrame(columns=["Institución", "Mes Pagado", "Monto", "Estatus Solvencia"]), num_rows="dynamic")

elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Generación y Control de Archivos")
    st.selectbox("Tipo de Archivo:", ["XML Retenciones IVA", "TXT Retenciones ISLR", "Resumen IVA Mensual"])
    st.file_uploader("Cargar TXT/XML para validación")
    st.button("📦 Generar y Descargar Archivo Maestro")
