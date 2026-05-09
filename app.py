import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. BLOQUEO DE INTERFAZ Y ESTILOS PROFESIONALES
st.set_page_config(page_title="SISTEMA VEN-PRO v80.0", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #fdfaf5 !important; }
    h1, h2, h3, p, label { color: #000000 !important; font-weight: 800 !important; }
    .stButton>button {
        width: 100% !important; border: 2px solid #000 !important; 
        background-color: #e8e8e8 !important; color: black !important; font-weight: bold;
    }
    .warning-pago { color: #FF0000 !important; font-weight: bold; animation: blinker 1.5s linear infinite; text-align: center; border: 2px solid red; padding: 10px; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZACIÓN DE BASE DE DATOS (TODO EN CERO PARA VENDER)
if 'auth' not in st.session_state: st.session_state.auth = False
if 'db_clientes' not in st.session_state: st.session_state.db_clientes = {} 
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = {}
if 'libros_data' not in st.session_state:
    # Estructura de datos para libros (Compras, Ventas, Diario-Mayor)
    st.session_state.libros_data = {
        "compras": pd.DataFrame(columns=["Fecha", "RIF Emisor", "Nombre/Razón Social", "Nro Factura", "Base Imponible", "IVA (16%)", "Total"]),
        "ventas": pd.DataFrame(columns=["Fecha", "RIF Receptor", "Nombre Cliente", "Nro Factura", "Base Imponible", "IVA (16%)", "Total"]),
        "diario_mayor": pd.DataFrame(columns=["Fecha", "Cuenta Contable", "Descripción Asiento", "Debe", "Haber", "Saldo"])
    }

# 3. PANTALLA DE ACCESO (LOGIN)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 SISTEMA CONTABLE VEN-PRO v80</h1>", unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 1.2, 1])
    with centro:
        with st.form("login_form"):
            st.subheader("🔐 Ingreso Protegido")
            user_input = st.text_input("USUARIO / RIF:").upper()
            pass_input = st.text_input("CONTRASEÑA:", type="password")
            st.write("---")
            if st.form_submit_button("🔓 ACCEDER"):
                if user_input == "ADMIN" and pass_input == "ADMIN123":
                    st.session_state.auth, st.session_state.rol, st.session_state.user = True, "ADMIN", user_input
                    st.rerun()
                elif user_input in st.session_state.db_clientes and st.session_state.db_clientes[user_input]["clave"] == pass_input:
                    if st.session_state.db_clientes[user_input]["estatus"] == "Activo":
                        st.session_state.auth, st.session_state.rol, st.session_state.user = True, "CLIENTE", user_input
                        st.rerun()
                    else: st.error("❌ ACCESO DENEGADO: Contacte a soporte para activar su mensualidad.")
                else: st.error("❌ Usuario o Clave inválidos.")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL Y CONTROL)
with st.sidebar:
    st.title(f"👤 {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.user]["vencimiento"], "%Y-%m-%d")
        dias_rest = (venc - datetime.now()).days
        if dias_rest <= 5:
            st.markdown(f"<p class='warning-pago'>⚠️ ADVERTENCIA:<br>SU MES VENCE EN {dias_rest} DÍAS<br>({venc.date()})</p>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes de Consulta:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=datetime.now().month - 1)
    h_anio = st.selectbox("Año de Consulta:", [2024, 2025, 2026], index=2)
    st.write("---")
    
    modulos = ["📊 DASHBOARD", "🏢 GESTIÓN +100 EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA (CONTROL)", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": modulos.insert(1, "👑 PANEL ADMINISTRADOR")
    
    menu = st.radio("SECCIONES:", modulos)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. LÓGICA DE VACIADO AUTOMÁTICO (PROCESAMIENTO DE IMAGEN/PDF)
def vaciar_datos_ia(archivo, tipo_libro):
    # Simulación de extracción de datos de la factura/documento
    datos_extraidos = {
        "Fecha": str(date.today()), "RIF": "J-99999999-0", "Nombre": "EXTRACCIÓN AUTOMÁTICA C.A",
        "Factura": "0001", "Base": 1000.00, "IVA": 160.00, "Total": 1160.00
    }
    if tipo_libro == "compras":
        nueva_fila = pd.DataFrame([[datos_extraidos["Fecha"], datos_extraidos["RIF"], datos_extraidos["Nombre"], datos_extraidos["Factura"], datos_extraidos["Base"], datos_extraidos["IVA"], datos_extraidos["Total"]]], columns=st.session_state.libros_data["compras"].columns)
        st.session_state.libros_data["compras"] = pd.concat([st.session_state.libros_data["compras"], nueva_fila], ignore_index=True)
    return datos_extraidos

# 6. MÓDULOS DEL SISTEMA
st.title(f"{menu} - Periodo: {h_mes} {h_anio}")

if menu == "👑 PANEL ADMINISTRADOR":
    st.subheader("Control Maestro de Suscriptores")
    with st.expander("➕ REGISTRAR NUEVO CLIENTE (DAR ACCESO)"):
        c1, c2, c3 = st.columns(3)
        user_new = c1.text_input("RIF/Usuario Cliente:")
        pass_new = c2.text_input("Clave de Acceso:")
        venc_new = c3.date_input("Fecha Vencimiento:", value=date(2026, 5, 30))
        if st.button("Habilitar Cliente"):
            st.session_state.db_clientes[user_new] = {"clave": pass_new, "estatus": "Activo", "vencimiento": str(venc_new)}
            st.success(f"Cliente {user_new} habilitado.")

    st.write("### Lista de Clientes y Estado de Pagos")
    for cli, info in st.session_state.db_clientes.items():
        col_a, col_b, col_c = st.columns([2, 1, 1])
        col_a.write(f"**Cliente:** {cli} (Vence: {info['vencimiento']})")
        nuevo_est = col_b.selectbox(f"Estatus", ["Activo", "Inactivo"], index=0 if info["estatus"]=="Activo" else 1, key=f"est_{cli}")
        st.session_state.db_clientes[cli]["estatus"] = nuevo_est
        if col_c.button("Eliminar", key=f"del_{cli}"):
            del st.session_state.db_clientes[cli]
            st.rerun()

elif menu == "🏢 GESTIÓN +100 EMPRESAS":
    st.subheader("Registro de Carteras de Contabilidad")
    with st.form("emp_reg"):
        n_e = st.text_input("Razón Social de la Empresa:")
        r_e = st.text_input("RIF de la Empresa:")
        if st.form_submit_button("💾 Guardar Empresa"):
            st.session_state.db_empresas[r_e] = {"Nombre": n_e, "Fecha_Alta": str(date.today())}
            st.success("Empresa añadida a la cartera.")
    st.write(f"Empresas en sistema: {len(st.session_state.db_empresas)} / 100")
    st.table(pd.DataFrame.from_dict(st.session_state.db_empresas, orient='index'))

elif menu == "🛒 LIBRO DE COMPRAS":
    st.subheader("Vaciado Automático y Registro de Compras")
    up = st.file_uploader("📥 CARGAR FACTURA (PDF/EXCEL/FOTO)", type=['pdf','png','jpg','xlsx'], help="La información se vaciará automáticamente abajo.")
    if up:
        if st.button("🚀 PROCESAR Y VACIAR AHORA"):
            vaciar_datos_ia(up, "compras")
            st.success("✅ ¡Vaciado completo! Revisa la tabla de abajo.")
    
    st.write("---")
    st.subheader("Tabla de Registro (Manual / Automático)")
    st.session_state.libros_data["compras"] = st.data_editor(st.session_state.libros_data["compras"], num_rows="dynamic", use_container_width=True)

elif menu == "💰 LIBRO DE VENTAS":
    st.subheader("Registro de Ventas del Periodo")
    st.file_uploader("📥 Cargar Reporte de Ventas / Facturas", type=['pdf','png','jpg','xlsx'])
    st.session_state.libros_data["ventas"] = st.data_editor(st.session_state.libros_data["ventas"], num_rows="dynamic", use_container_width=True)

elif menu == "📖 DIARIO Y MAYOR":
    st.subheader("Libro Diario y Mayor Integrado")
    st.file_uploader("📥 Cargar Movimientos Bancarios", type=['pdf','xlsx'])
    st.write("### Asientos Contables")
    st.session_state.libros_data["diario_mayor"] = st.data_editor(st.session_state.libros_data["diario_mayor"], num_rows="dynamic", use_container_width=True)

elif menu == "🏛️ ALCALDÍA (CONTROL)":
    st.info("📍 Municipio Girardot y otros - Control de Impuestos Municipales")
    impuesto = st.selectbox("Impuesto a Gestionar:", ["IAE/ISAE (Actividades Económicas)", "Derecho de Frente", "Vehículos", "Publicidad", "Espectáculos", "ASEO (Sateca)"])
    st.file_uploader(f"Subir Comprobante de Pago para {impuesto}")
    st.write("### Control Manual de Pagos Municipales")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Tributo", "Monto Bs.", "Nro Referencia", "Soporte"]), num_rows="dynamic", use_container_width=True)

elif menu == "🏢 PARAFISCALES":
    st.subheader("Control de Aportes Patronales")
    inst = st.selectbox("Seleccione Ente:", ["IVSS", "FAOV (BANAVIH)", "INCES", "Régimen Empleo", "Nueva Ley de Pensiones (2025)"])
    st.file_uploader(f"Cargar Planilla / Pago de {inst}")
    st.write("### Registro de Solvencias")
    st.data_editor(pd.DataFrame(columns=["Mes", "Institución", "Monto", "Referencia"]), num_rows="dynamic", use_container_width=True)

elif menu == "📤 SENIAT (XML/TXT)":
    st.subheader("Generación y Auditoría de Archivos Fiscales")
    st.selectbox("Tipo de Archivo:", ["XML Retenciones IVA", "TXT Retenciones ISLR", "Carga de Facturas SENIAT"])
    st.file_uploader("📥 Cargar XML/TXT anterior para control de pagos")
    st.button("📦 GENERAR ARCHIVO MAESTRO")
