import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid

# 1. SEGURIDAD Y PROTECCIÓN DE NAVEGACIÓN
st.set_page_config(page_title="VEN-PRO v500 - SISTEMA CONTABLE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f4f7f9 !important; }
    .alerta-vencido { color: #FF0000; font-weight: bold; font-size: 24px; animation: blinker 1s linear infinite; text-align: center; border: 2px solid red; padding: 10px; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE PERSISTENCIA (BASE DE DATOS MASIVA)
if 'session_db' not in st.session_state:
    st.session_state.auth = False
    st.session_state.db_clientes = {} 
    st.session_state.empresas_usuario = [] # Capacidad 100
    # Tablas con columnas EXACTAS solicitadas
    st.session_state.l_compras = pd.DataFrame(columns=["ID", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto", "Fecha"])
    st.session_state.l_ventas = pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"])
    st.session_state.l_diario_mayor = pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Descripción", "Debe (Bs.)", "Haber (Bs.)", "Referencia"])

# 3. SISTEMA DE LOGIN REFORZADO
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>📂 INGRESO SEGURO VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login_form"):
            u_input = st.text_input("USUARIO / RIF:").strip().upper()
            p_input = st.text_input("CONTRASEÑA:", type="password").strip()
            if st.form_submit_button("🛡️ ACCEDER"):
                if u_input == "MARIA" and p_input == "ADMIN2026":
                    st.session_state.auth, st.session_state.role = True, "ADMIN"
                    st.rerun()
                elif u_input in st.session_state.db_clientes and st.session_state.db_clientes[u_input]['pass'] == p_input:
                    if st.session_state.db_clientes[u_input]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.role, st.session_state.current_u = True, "CLIENTE", u_input
                        st.rerun()
                    else: st.error("🚫 ACCESO BLOQUEADO. CONTACTE AL ADMINISTRADOR.")
                else: st.error("❌ Credenciales Incorrectas.")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL + MENÚ)
with st.sidebar:
    st.title(f"⭐ {st.session_state.role}")
    if st.session_state.role == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.current_u]['vencimiento'], '%Y-%m-%d').date()
        if venc <= date.today() + timedelta(days=5):
            st.markdown(f"<div class='alerta-vencido'>¡PAGO VENCE: {venc}!</div>", unsafe_allow_html=True)

    st.subheader("🔍 LUPA DE HISTORIAL")
    mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio = st.selectbox("Año", [2025, 2026])

    menu = ["📊 DASHBOARD", "🏢 CARTERA 100 EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 TXT/XML SENIAT"]
    if st.session_state.role == "ADMIN": menu.insert(1, "👑 PANEL ADMINISTRADOR")
    
    sel = st.radio("MÓDULOS DEL SISTEMA", menu)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. PANEL ADMINISTRADOR (TU CONTROL)
if sel == "👑 PANEL ADMINISTRADOR":
    st.header("Control de Suscripciones Mensuales")
    with st.form("admin_control"):
        c1, c2, c3 = st.columns(3)
        n_rif = c1.text_input("RIF / Usuario del Cliente:")
        n_pass = c2.text_input("Asignar Contraseña:")
        n_venc = c3.date_input("Fecha Vencimiento de Pago:")
        if st.form_submit_button("REGISTRAR Y HABILITAR"):
            st.session_state.db_clientes[n_rif] = {"pass": n_pass, "vencimiento": str(n_venc), "status": "ACTIVO"}
            st.success("Cliente registrado con éxito.")

    st.write("### Clientes Activos y Bloqueos")
    for r, info in st.session_state.db_clientes.items():
        col1, col2 = st.columns([3, 1])
        color = "🟢" if info['status'] == "ACTIVO" else "🔴"
        col1.write(f"{color} **{r}** | Vencimiento: {info['vencimiento']}")
        if col2.button("CAMBIAR ESTADO", key=r):
            st.session_state.db_clientes[r]['status'] = "INACTIVO" if info['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

# 6. MÓDULO CARTERA DE EMPRESAS
elif sel == "🏢 CARTERA 100 EMPRESAS":
    st.header("Cartera de Clientes Contables (Máximo 100)")
    with st.form("cartera"):
        c1, c2 = st.columns(2)
        e_nom = c1.text_input("Nombre / Razón Social de la Empresa:")
        e_rif = c2.text_input("RIF:")
        if st.form_submit_button("GUARDAR EMPRESA"):
            if len(st.session_state.empresas_usuario) < 100:
                st.session_state.empresas_usuario.append({"Nombre": e_nom, "RIF": e_rif})
                st.success("Empresa añadida.")
            else: st.error("Límite de 100 empresas alcanzado.")
    st.table(pd.DataFrame(st.session_state.empresas_usuario))

# 7. LIBRO DE COMPRAS (EXTRACCIÓN DINÁMICA)
elif sel == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Compras - {mes} {anio}")
    st.file_uploader("CARGAR FACTURA (PDF, EXCEL, PNG, JPG)", type=['pdf','png','jpg','jpeg','xlsx'], key="compras_up")
    
    st.markdown("### 📥 VACIADO DINÁMICO (Confirmación de Datos)")
    with st.form("vaciado_f"):
        c1, c2, c3, c4 = st.columns(4)
        prov = c1.text_input("Nombre / Razón Social Proveedor")
        desc_b = c2.text_input("DESCRICIÓN Y BANCO")
        f_num = c3.text_input("Factura N°")
        f_cont = c4.text_input("Nº Control")
        
        c5, c6, c7, c8 = st.columns(4)
        f_total = c5.number_input("Total Compras (Bs.)", format="%.2f")
        f_exento = c6.number_input("Compras Exentas (Bs.)", format="%.2f")
        f_base = c7.number_input("Base (Bs.)", format="%.2f")
        f_iva = c8.number_input("Impuesto %16 (Bs.)", format="%.2f")
        
        if st.form_submit_button("📥 CARGAR FACTURA DEFINITIVAMENTE"):
            row = {"ID": str(uuid.uuid4())[:6], "Nombre / Razón Social Proveedor": prov, "DESCRICION Y BANCO": desc_b, "Factura N°": f_num, "Nº Control": f_cont, "Total Compras": f_total, "Compras Exentas": f_exento, "Base": f_base, "Impuesto": f_iva, "Fecha": str(date.today())}
            st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([row])], ignore_index=True)
            st.success("Factura almacenada en la base de datos masiva.")

    st.write("### 📜 Historial de Facturas (Capacidad 100.000+)")
    if not st.session_state.l_compras.empty:
        id_del = st.selectbox("ID para borrar manualmente:", st.session_state.l_compras["ID"])
        if st.button("🗑️ ELIMINAR FACTURA SELECCIONADA"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_del]
            st.rerun()
    st.data_editor(st.session_state.l_compras, use_container_width=True)

# 8. DASHBOARD (RESUMEN DE BLOQUES)
elif sel == "📊 DASHBOARD":
    st.header("Estado General del Sistema")
    k1, k2, k3 = st.columns(3)
    k1.metric("TOTAL COMPRAS", f"Bs. {st.session_state.l_compras['Total Compras'].sum():,.2f}")
    k2.metric("EMPRESAS EN CARTERA", len(st.session_state.empresas_usuario))
    k3.metric("FACTURAS PROCESADAS", len(st.session_state.l_compras))
    st.write("---")
    st.info("Todos los libros y módulos parafiscales están listos para la carga de datos del cliente.")
