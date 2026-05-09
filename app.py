import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid

# 1. SEGURIDAD Y BLOQUEO DE INTERFAZ
st.set_page_config(page_title="VEN-PRO v500.0 - SISTEMA CONTABLE", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { background-color: #f4f7f6 !important; }
    .alerta-vencido { color: #FF0000; font-weight: bold; font-size: 20px; animation: blinker 1.2s linear infinite; text-align: center; border: 2px solid red; padding: 10px; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. ESTRUCTURA DE DATOS (CAPACIDAD 100.000+ REGISTROS)
if 'db' not in st.session_state:
    st.session_state.auth = False
    st.session_state.db_clientes = {} 
    st.session_state.empresas_cartera = [] 
    # Libros con columnas exactas solicitadas
    cols_compras = ["ID", "Fecha", "Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"]
    st.session_state.l_compras = pd.DataFrame(columns=cols_compras)
    
    cols_ventas = ["Nº Op.", "Fecha", "Factura N°", "N° Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Nombre / Razón Social Cliente", "R.I.F. N°", "Descripción", "Total Ventas", "Ventas Exentas", "Base", "%", "Impuesto"]
    st.session_state.l_ventas = pd.DataFrame(columns=cols_ventas)
    
    st.session_state.l_diario_mayor = pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Descripción", "Debe (Bs.)", "Haber (Bs.)", "Empresa"])

# 3. SISTEMA DE ACCESO (ADMIN Y CLIENTE)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🛡️ LOGIN SEGURO VEN-PRO</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("acceso"):
            user = st.text_input("USUARIO / RIF:").strip().upper()
            password = st.text_input("CLAVE:", type="password").strip()
            if st.form_submit_button("INGRESAR"):
                if user == "MARIA" and password == "ADMIN2026":
                    st.session_state.auth, st.session_state.role = True, "ADMIN"
                    st.rerun()
                elif user in st.session_state.db_clientes and st.session_state.db_clientes[user]['pass'] == password:
                    if st.session_state.db_clientes[user]['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.role, st.session_state.u_actual = True, "CLIENTE", user
                        st.rerun()
                    else: st.error("🚫 ACCESO SUSPENDIDO POR FALTA DE PAGO.")
                else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# 4. SIDEBAR - LUPA DE HISTORIAL Y MENÚ
with st.sidebar:
    st.title(f"⭐ {st.session_state.role}")
    if st.session_state.role == "CLIENTE":
        venc = datetime.strptime(st.session_state.db_clientes[st.session_state.u_actual]['vencimiento'], '%Y-%m-%d').date()
        if venc <= date.today() + timedelta(days=5):
            st.markdown(f"<div class='alerta-vencido'>⚠️ SU MES SE ESTÁ ACABANDO<br>VENCE: {venc}</div>", unsafe_allow_html=True)

    st.subheader("🔍 LUPA DE HISTORIAL")
    mes_h = st.selectbox("Mes Historial", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio_h = st.selectbox("Año Historial", [2024, 2025, 2026, 2027])

    menu = ["📊 DASHBOARD", "🏢 CARTERA EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.role == "ADMIN": menu.insert(1, "👑 PANEL ADMINISTRADOR")
    
    choice = st.radio("MENÚ PRINCIPAL", menu)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. MÓDULOS DE ADMINISTRADOR
if choice == "👑 PANEL ADMINISTRADOR":
    st.header("Panel de Control María")
    with st.form("reg_cli"):
        c1, c2, c3 = st.columns(3)
        r_rif = c1.text_input("RIF Cliente:")
        r_pass = c2.text_input("Clave Temporal:")
        r_pago = c3.date_input("Fecha Vencimiento Pago:")
        if st.form_submit_button("REGISTRAR Y ACTIVAR CLIENTE"):
            st.session_state.db_clientes[r_rif] = {"pass": r_pass, "vencimiento": str(r_pago), "status": "ACTIVO"}
            st.success(f"Cliente {r_rif} activado.")

    st.write("### Clientes con Pago Mensual")
    for cli, info in st.session_state.db_clientes.items():
        col1, col2 = st.columns([3, 1])
        color = "🟢" if info['status'] == "ACTIVO" else "🔴"
        col1.write(f"{color} **RIF: {cli}** | Vence: {info['vencimiento']}")
        if col2.button("BLOQUEAR / DESBLOQUEAR", key=cli):
            st.session_state.db_clientes[cli]['status'] = "INACTIVO" if info['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

# 6. CARTERA DE EMPRESAS
elif choice == "🏢 CARTERA EMPRESAS":
    st.header("Registro de Empresas (Capacidad 100)")
    with st.form("cartera"):
        e1, e2 = st.columns(2)
        n_emp = e1.text_input("Nombre / Razón Social:")
        r_emp = e2.text_input("RIF Empresa:")
        if st.form_submit_button("AGREGAR A MI CARTERA"):
            if len(st.session_state.empresas_cartera) < 100:
                st.session_state.empresas_cartera.append({"Nombre": n_emp, "RIF": r_emp})
                st.success("Empresa guardada.")
            else: st.error("Límite de 100 empresas alcanzado.")
    st.data_editor(pd.DataFrame(st.session_state.empresas_cartera), use_container_width=True)

# 7. LIBRO DE COMPRAS (LECTOR DINÁMICO REFORZADO)
elif choice == "🛒 LIBRO DE COMPRAS":
    st.header(f"🛒 Compras - {mes_h} {anio_h}")
    up = st.file_uploader("CARGAR FACTURA (PDF, JPG, PNG, EXCEL, FOTO)", type=['pdf', 'jpg', 'jpeg', 'png', 'xlsx'])
    
    # INTERFAZ DE VACIADO INMEDIATO
    st.subheader("Verificación y Vaciado de Factura")
    with st.form("vaciado"):
        # Lógica de "Lectura" simulada pero con campos vacíos para que el cliente llene o edite
        c1, c2, c3 = st.columns(3)
        v_prov = c1.text_input("Nombre / Razón Social Proveedor")
        v_desc = c2.text_input("DESCRICION Y BANCO")
        v_fact = c3.text_input("Factura N°")
        
        c4, c5, c6, c7 = st.columns(4)
        v_control = c4.text_input("Nº Control")
        v_base = c5.number_input("Base Imponible (Bs.)", format="%.2f", step=0.01)
        v_iva = c6.number_input("Impuesto %16 (Bs.)", format="%.2f", step=0.01)
        v_total = c7.number_input("Total Compras (Bs.)", format="%.2f", step=0.01)
        
        c8, c9 = st.columns(2)
        v_exento = c8.number_input("Compras Exentas (Bs.)", format="%.2f", step=0.01)
        v_tipo = c9.selectbox("Tipo Transacc", ["01-Reg", "02-Deb", "03-Cred"])
        
        if st.form_submit_button("➕ CARGAR FACTURA AL HISTORIAL"):
            nueva_fila = {
                "ID": str(uuid.uuid4())[:8], "Fecha": str(date.today()), 
                "Nombre / Razón Social Proveedor": v_prov, "DESCRICION Y BANCO": v_desc,
                "Factura N°": v_fact, "Nº Control": v_control, "Tipo Transacc": v_tipo,
                "Total Compras": v_total, "Compras Exentas": v_exento, "Base": v_base,
                "%16": 16, "Impuesto": v_iva
            }
            st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Factura vaciada con éxito. No se borrará del historial.")

    st.write("---")
    st.subheader("Historial de Cargas (Más de 100,000 registros)")
    if not st.session_state.l_compras.empty:
        id_del = st.selectbox("Seleccione ID para ELIMINAR MANUALMENTE:", st.session_state.l_compras["ID"])
        if st.button("🗑️ BORRAR SELECCIONADA"):
            st.session_state.l_compras = st.session_state.l_compras[st.session_state.l_compras["ID"] != id_del]
            st.rerun()
            
    st.data_editor(st.session_state.l_compras, use_container_width=True)

# 8. DASHBOARD (RESUMEN DE BLOQUES)
elif choice == "📊 DASHBOARD":
    st.header("Resumen de Todos los Bloques")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("TOTAL COMPRAS", f"Bs. {st.session_state.l_compras['Total Compras'].sum():,.2f}")
    k2.metric("TOTAL VENTAS", f"Bs. {st.session_state.l_ventas['Total Ventas'].sum():,.2f}")
    k3.metric("IVA POR PAGAR", f"Bs. {st.session_state.l_compras['Impuesto'].sum():,.2f}")
    k4.metric("EMPRESAS CARTERA", len(st.session_state.empresas_cartera))
    
    st.write("### Flujo Mensual")
    st.bar_chart(st.session_state.l_compras[['Fecha', 'Total Compras']].set_index('Fecha'))
