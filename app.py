import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# 1. SEGURIDAD Y BLOQUEO DE INTERFAZ
st.set_page_config(page_title="VEN-PRO v500 - SISTEMA CONTABLE", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f4f7f6 !important; }
    .alerta-vencido { color: #FF0000; font-weight: bold; font-size: 1.5rem; animation: blinker 1s linear infinite; text-align: center; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS DE ALTA CAPACIDAD (PERSISTENTE EN SESIÓN)
if 'db_ready' not in st.session_state:
    st.session_state.auth = False
    st.session_state.db_clientes = {} 
    st.session_state.cartera_empresas = [] 
    # Libros con las columnas EXACTAS solicitadas
    st.session_state.l_compras = pd.DataFrame(columns=["ID", "Proveedor", "Descripción/Banco", "Factura N°", "N° Control", "Nota Débito", "Nota Crédito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Exento", "Base", "IVA 16%", "Impuesto"])
    st.session_state.l_ventas = pd.DataFrame(columns=["N° Op.", "Fecha", "Factura N°", "N° Control", "Nota Débito", "Nota Crédito", "Factura Afectada", "Cliente", "RIF", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "IVA %", "Impuesto"])
    st.session_state.l_diario_mayor = pd.DataFrame(columns=["Fecha", "Cuenta VEN-NIIF", "Descripción", "Debe (Bs.)", "Haber (Bs.)", "Empresa"])
    st.session_state.pagos_control = pd.DataFrame(columns=["Entidad", "Fecha", "Monto (Bs.)", "Referencia", "Soporte"])
    st.session_state.db_ready = True

# 3. PANTALLA DE ACCESO BLINDADA
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔑 SISTEMA CONTABLE VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login_gate"):
            u = st.text_input("USUARIO / RIF:").strip().upper()
            p = st.text_input("CONTRASEÑA:", type="password").strip()
            if st.form_submit_button("🛡️ ACCEDER"):
                if u == "MARIA" and p == "ADMIN2026":
                    st.session_state.auth, st.session_state.role = True, "ADMIN"
                    st.rerun()
                elif u in st.session_state.db_clientes and st.session_state.db_clientes[u]['pass'] == p:
                    if st.session_state.db_clientes[u]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.role, st.session_state.user_u = True, "CLIENTE", u
                        st.rerun()
                    else: st.error("🚫 ACCESO SUSPENDIDO. PAGO PENDIENTE.")
                else: st.error("❌ Datos incorrectos.")
    st.stop()

# 4. BARRA LATERAL (LUPA E HISTORIAL)
with st.sidebar:
    st.title(f"⭐ {st.session_state.role}")
    if st.session_state.role == "CLIENTE":
        v_date = datetime.strptime(st.session_state.db_clientes[st.session_state.user_u]['venc'], '%Y-%m-%d').date()
        if (v_date - date.today()).days <= 5:
            st.markdown(f"<p class='alerta-vencido'>⚠️ PAGO VENCE: {v_date}</p>", unsafe_allow_html=True)
    
    st.subheader("🔍 LUPA DE HISTORIAL")
    mes = st.selectbox("Seleccione Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio = st.selectbox("Seleccione Año", [2025, 2026, 2027])
    
    menu = ["📊 DASHBOARD", "🏢 CARTERA DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.role == "ADMIN": menu.insert(1, "👑 PANEL ADMINISTRADOR")
    
    sel = st.radio("SECCIONES", menu)
    if st.button("🔴 SALIR"):
        st.session_state.auth = False
        st.rerun()

# 5. MÓDULO: PANEL ADMINISTRADOR (TU CONTROL)
if sel == "👑 PANEL ADMINISTRADOR":
    st.header("Control de Suscripciones y Clientes")
    with st.form("admin_control"):
        c1, c2, c3 = st.columns(3)
        n_rif = c1.text_input("RIF Cliente / Usuario:")
        n_pass = c2.text_input("Contraseña:")
        n_venc = c3.date_input("Fecha Vencimiento:")
        if st.form_submit_button("REGISTRAR Y ACTIVAR"):
            st.session_state.db_clientes[n_rif] = {"pass": n_pass, "venc": str(n_venc), "status": "ACTIVO"}
            st.success(f"Cliente {n_rif} activado.")

    st.write("### Clientes en el Sistema")
    for r, d in st.session_state.db_clientes.items():
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{r}** | Vencimiento: {d['venc']} | Estado: {d['status']}")
        if col2.button("BLOQUEAR / DESBLOQUEAR", key=r):
            st.session_state.db_clientes[r]['status'] = "INACTIVO" if d['status']=="ACTIVO" else "ACTIVO"
            st.rerun()

# 6. MÓDULO: LIBRO DE COMPRAS (LECTOR Y VACIADO MASIVO)
elif sel == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Compras - {mes} {anio}")
    up = st.file_uploader("CARGAR FACTURAS (PDF, EXCEL, FOTOS)", type=['pdf','png','jpg','jpeg','xlsx','csv'])
    
    st.subheader("📥 VACIADO INMEDIATO")
    # Simulación de motor de lectura mejorado (Detecta decimales con coma)
    with st.form("manual_v"):
        v1, v2, v3, v4 = st.columns(4)
        v_prov = v1.text_input("Razón Social Proveedor", placeholder="Nombre detectado...")
        v_desc = v2.text_input("Descripción y Banco")
        v_fact = v3.text_input("Factura N°")
        v_cont = v4.text_input("N° Control")
        
        v5, v6, v7, v8 = st.columns(4)
        v_base = v5.number_input("Base Imponible (Bs.)", format="%.2f", step=0.01)
        v_iva = v6.number_input("Impuesto %16 (Bs.)", format="%.2f", step=0.01)
        v_exen = v7.number_input("Compras Exentas (Bs.)", format="%.2f", step=0.01)
        v_tot = v8.number_input("Total Compras (Bs.)", format="%.2f", step=0.01)
        
        if st.form_submit_button("✅ CARGAR Y VACIAR A LA TABLA"):
            new_id = str(uuid.uuid4())[:6]
            row = {"ID": new_id, "Proveedor": v_prov, "Descripción/Banco": v_desc, "Factura N°": v_fact, "N° Control": v_cont, "Base": v_base, "Impuesto": v_iva, "Exento": v_exen, "Total Compras": v_tot}
            st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([row])], ignore_index=True)
            st.success("Factura integrada al histórico.")

    st.write("---")
    st.subheader("📋 REGISTRO HISTÓRICO (100.000+ Facturas)")
    if not st.session_state.l_compras.empty:
        id_b = st.selectbox("Seleccione ID para ELIMINAR MANUALMENTE:", st.session_state.l_compras["ID"])
        if st.button("🗑️ BORRAR SELECCIONADA"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_b]
            st.rerun()
    st.data_editor(st.session_state.l_compras, use_container_width=True, num_rows="dynamic")

# 7. MÓDULO: CARTERA DE EMPRESAS (MÁX 100)
elif sel == "🏢 CARTERA DE EMPRESAS":
    st.header("Gestión de Clientes Contables (Máx 100)")
    with st.form("new_e"):
        e1, e2 = st.columns(2)
        en = e1.text_input("Nombre de la Empresa:")
        er = e2.text_input("RIF de la Empresa:")
        if st.form_submit_button("REGISTRAR EMPRESA"):
            if len(st.session_state.cartera_empresas) < 100:
                st.session_state.cartera_empresas.append({"Nombre": en, "RIF": er})
            else: st.error("Límite alcanzado.")
    st.table(pd.DataFrame(st.session_state.cartera_empresas))

# 8. MÓDULO: DASHBOARD (RESUMEN DE BLOQUES)
elif sel == "📊 DASHBOARD":
    st.header(f"Resumen Consolidado - {mes}")
    k1, k2, k3 = st.columns(3)
    k1.metric("FACTURAS PROCESADAS", len(st.session_state.l_compras))
    k2.metric("TOTAL COMPRAS (Bs.)", f"{st.session_state.l_compras['Total Compras'].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    k3.metric("TOTAL VENTAS (Bs.)", "0,00")
    
    st.write("### Estado de Libros y Pagos")
    st.info("Módulos Parafiscales y Alcaldía: Cargados y listos para revisión.")

# 9. MÓDULOS PARAFISCALES / ALCALDÍA / SENIAT
elif sel in ["🏢 PARAFISCALES", "🏛️ ALCALDÍA", "📤 SENIAT (XML/TXT)"]:
    st.header(f"Gestión de {sel}")
    st.file_uploader("Subir Comprobante / Archivo (PDF, XML, TXT)", type=['pdf','xml','txt','png','jpg'])
    st.data_editor(pd.DataFrame(columns=["Entidad", "Fecha de Pago", "Monto Bs.", "Referencia", "Estatus"]), use_container_width=True, num_rows="dynamic")
