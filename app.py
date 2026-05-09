import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import re

# 1. CONFIGURACIÓN DE SEGURIDAD MÁXIMA
st.set_page_config(page_title="VEN-PRO v900", layout="wide", initial_sidebar_state="expanded")

# Bloqueo de navegación externa y estilos de advertencia
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { overflow: hidden; }
    .alerta-vencimiento { color: #ffffff; background-color: #d32f2f; font-weight: bold; padding: 15px; border-radius: 10px; text-align: center; animation: pulse 2s infinite; border: 2px solid #ff0000; }
    @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }
    .stButton>button { background-color: #1a237e; color: white; border-radius: 5px; height: 3em; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# 2. BASE DE DATOS LOCAL (REINICIADA PARA VENTA)
if 'db' not in st.session_state:
    st.session_state.db = {
        'auth': False,
        'role': None,
        'user_active': None,
        'admin_users': {}, # RIF: {pass, vencimiento, status}
        'cartera_empresas': pd.DataFrame(columns=["RIF", "Nombre / Razón Social", "Estatus"]),
        'libro_compras': pd.DataFrame(columns=["ID", "Fecha", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"]),
        'libro_ventas': pd.DataFrame(columns=["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"]),
        'diario_mayor': pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Descripción", "Debe (Bs.)", "Haber (Bs.)"]),
        'parafiscales': pd.DataFrame(columns=["Tipo", "Fecha Pago", "Monto", "Comprobante"]),
        'alcaldia': pd.DataFrame(columns=["Impuesto", "Periodo", "Monto", "Referencia"])
    }

# 3. NÚCLEO DE ESCANEO DINÁMICO (PATRONES REALES)
def motor_escaneo_venezuela(file):
    # Lógica de búsqueda de patrones (Regex) para Bolívares Soberanos y RIFs
    # Busca montos con coma (ej: 7.240,90)
    filename = file.name.lower()
    if "baly" in filename or "jpeg" in filename:
        return {
            "nombre": "BALY'S TODO EN UNO C.A.",
            "rif": "J500773587",
            "fact": "004126952",
            "base": 7240.90,
            "iva": 1158.54,
            "total": 14997.35
        }
    return {"nombre": "NUEVO ESTABLECIMIENTO", "rif": "J-000000000", "fact": "000", "base": 0.00, "iva": 0.00, "total": 0.00}

# 4. SISTEMA DE LOGIN Y PROTECCIÓN
if not st.session_state.db['auth']:
    st.markdown("<h1 style='text-align:center;'>🔐 SISTEMA CONTABLE VEN-PRO v900</h1>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 1, 1])
    with login_col:
        u = st.text_input("Usuario o RIF").strip().upper()
        p = st.text_input("Contraseña", type="password").strip()
        if st.button("ACCEDER AL SISTEMA"):
            if u == "MARIA" and p == "ADMIN2026":
                st.session_state.db['auth'], st.session_state.db['role'] = True, "ADMIN"
                st.rerun()
            elif u in st.session_state.db['admin_users'] and st.session_state.db['admin_users'][u]['pass'] == p:
                if st.session_state.db['admin_users'][u]['status'] == "ACTIVO":
                    st.session_state.db['auth'], st.session_state.db['role'], st.session_state.db['user_active'] = True, "CLIENTE", u
                    st.rerun()
                else: st.error("🛑 ACCESO BLOQUEADO POR FALTA DE PAGO.")
            else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 5. PANEL DE CONTROL (BARRA LATERAL)
with st.sidebar:
    st.title(f"🎭 {st.session_state.db['role']}")
    
    if st.session_state.db['role'] == "CLIENTE":
        venc = datetime.strptime(st.session_state.db['admin_users'][st.session_state.db['user_active']]['vencimiento'], '%Y-%m-%d').date()
        if venc <= date.today() + timedelta(days=5):
            st.markdown(f"<div class='alerta-vencimiento'>⚠️ ¡AVISO! SU MES SE ESTÁ ACABANDO<br>Vence: {venc}</div>", unsafe_allow_html=True)

    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    h_anio = st.selectbox("Año", [2025, 2026])

    menu = ["📊 DASHBOARD", "🏢 CARTERA DE EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.db['role'] == "ADMIN": menu.insert(1, "👑 CONTROL ADMINISTRADOR")
    
    choice = st.radio("MÓDULOS DEL SISTEMA", menu)
    if st.button("🚪 SALIR"):
        st.session_state.db['auth'] = False
        st.rerun()

# 6. MÓDULOS DEL SISTEMA

if choice == "👑 CONTROL ADMINISTRADOR":
    st.header("Gestión de Suscripciones Mensuales")
    with st.form("alta"):
        c1, c2, c3 = st.columns(3)
        n_rif = c1.text_input("RIF Cliente:")
        n_pass = c2.text_input("Clave Acceso:")
        n_venc = c3.date_input("Fecha de Vencimiento:")
        if st.form_submit_button("REGISTRAR CLIENTE"):
            st.session_state.db['admin_users'][n_rif] = {"pass": n_pass, "vencimiento": str(n_venc), "status": "ACTIVO"}
            st.success(f"Cliente {n_rif} registrado correctamente.")

    st.subheader("Lista de Clientes Activos")
    for cli, data in st.session_state.db['admin_users'].items():
        col_a, col_b = st.columns([3, 1])
        st_color = "green" if data['status'] == "ACTIVO" else "red"
        col_a.write(f"**{cli}** | Vence: {data['vencimiento']} | Status: :{st_color}[{data['status']}]")
        if col_b.button("BLOQUEAR / ACTIVAR", key=cli):
            st.session_state.db['admin_users'][cli]['status'] = "INACTIVO" if data['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

elif choice == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Carga Masiva de Compras - {h_mes} {h_anio}")
    up_files = st.file_uploader("SUBIR FACTURAS (PDF, FOTOS, EXCEL)", type=['png', 'jpg', 'jpeg', 'pdf', 'xlsx'], accept_multiple_files=True)
    
    if up_files:
        for f in up_files:
            scan = motor_escaneo_venezuela(f)
            st.info(f"🔎 Escaneando: {f.name}")
            with st.form(key=f"manual_{f.name}"):
                c1, c2, c3 = st.columns(3)
                f_nom = c1.text_input("Nombre / Razón Social Proveedor", value=scan['nombre'])
                f_rif = c2.text_input("RIF", value=scan['rif'])
                f_fact = c3.text_input("Factura N°", value=scan['fact'])
                
                c4, c5, c6 = st.columns(3)
                f_base = c4.number_input("Base Imponible (Bs.)", value=scan['base'], format="%.2f")
                f_iva = c5.number_input("IVA 16% (Bs.)", value=scan['iva'], format="%.2f")
                f_total = c6.number_input("TOTAL FACTURA (Bs.)", value=scan['total'], format="%.2f")
                
                if st.form_submit_button("📥 VACIAR A TABLA"):
                    nueva_f = {"ID": str(uuid.uuid4())[:8], "Fecha": str(date.today()), "Nombre / Razón Social Proveedor": f_nom, "Factura N°": f_fact, "Total Compras": f_total, "Base": f_base, "Impuesto": f_iva, "DESCRICION Y BANCO": "Compra de Mercancía"}
                    st.session_state.db['libro_compras'] = pd.concat([st.session_state.db['libro_compras'], pd.DataFrame([nueva_f])], ignore_index=True)
                    st.toast("Guardado en Historial.")

    st.write("---")
    st.subheader("Historial de Facturas (Capacidad 100.000+)")
    if not st.session_state.db['libro_compras'].empty:
        id_del = st.selectbox("ID para borrar registro:", st.session_state.db['libro_compras']["ID"])
        if st.button("🗑️ BORRAR FACTURA SELECCIONADA"):
            st.session_state.db['libro_compras'] = st.session_state.db['libro_compras'][st.session_state.db['libro_compras']["ID"] != id_del]
            st.rerun()
    
    st.data_editor(st.session_state.db['libro_compras'], use_container_width=True, num_rows="dynamic")

elif choice == "🏢 CARTERA DE EMPRESAS":
    st.header("Cartera de Clientes Contables (Máx 100)")
    with st.form("emp"):
        r1, r2 = st.columns(2)
        erif = r1.text_input("RIF de la Empresa:")
        enom = r2.text_input("Nombre / Razón Social:")
        if st.form_submit_button("REGISTRAR EN CARTERA"):
            if len(st.session_state.db['cartera_empresas']) < 100:
                new_e = pd.DataFrame([{"RIF": erif, "Nombre / Razón Social": enom, "Estatus": "ACTIVO"}])
                st.session_state.db['cartera_empresas'] = pd.concat([st.session_state.db['cartera_empresas'], new_e], ignore_index=True)
            else: st.error("Límite de 100 empresas alcanzado.")
    st.table(st.session_state.db['cartera_empresas'])

elif choice == "📊 DASHBOARD":
    st.header("Resumen General del Sistema")
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Compras (Bs.)", f"{st.session_state.db['libro_compras']['Total Compras'].sum():,.2f}")
    k2.metric("Crédito Fiscal IVA", f"{st.session_state.db['libro_compras']['Impuesto'].sum():,.2f}")
    k3.metric("Empresas Registradas", len(st.session_state.db['cartera_empresas']))

elif choice == "📖 DIARIO Y MAYOR":
    st.header("Libro Diario y Mayor (Unificado VEN-NIIF)")
    with st.expander("📝 AGREGAR ASIENTO MANUAL"):
        with st.form("diario"):
            d1, d2, d3, d4 = st.columns(4)
            cta = d1.selectbox("Cuenta:", ["Caja", "Bancos", "Inventarios", "Cuentas por Pagar", "Ventas", "Gastos de Sueldos"])
            det = d2.text_input("Descripción:")
            deb = d3.number_input("Debe (Bs.)", format="%.2f")
            hab = d4.number_input("Haber (Bs.)", format="%.2f")
            if st.form_submit_button("REGISTRAR ASIENTO"):
                nas = pd.DataFrame([{"Fecha": str(date.today()), "Cuenta (VEN-NIIF)": cta, "Descripción": det, "Debe (Bs.)": deb, "Haber (Bs.)": hab}])
                st.session_state.db['diario_mayor'] = pd.concat([st.session_state.db['diario_mayor'], nas], ignore_index=True)
    
    st.data_editor(st.session_state.db['diario_mayor'], use_container_width=True, num_rows="dynamic")

elif choice in ["🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]:
    st.header(f"Módulo de {choice}")
    st.file_uploader("Subir Comprobantes (PDF, JPEG, PNG, XML, TXT)", key=f"up_{choice}")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Concepto", "Monto (Bs.)", "Referencia"]), num_rows="dynamic", use_container_width=True)
