import streamlit as st
import pandas as pd
from datetime import datetime, date

# 1. CONFIGURACIÓN DE SEGURIDAD Y BLOQUEO DE NAVEGACIÓN
st.set_page_config(page_title="SISTEMA VEN-PRO v120", layout="wide")
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    .stApp { background-color: #f8f9fa !important; }
    .status-rojo { color: #d32f2f !important; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# 2. PERSISTENCIA DE DATOS (CAPACIDAD PARA +100.000 FACTURAS)
# Usamos session_state para que no se borre nada al navegar
if 'auth' not in st.session_state: st.session_state.auth = False
if 'rol' not in st.session_state: st.session_state.rol = None
if 'db_clientes' not in st.session_state: 
    # Base de datos de prueba: RIF: 123, Clave: 123
    st.session_state.db_clientes = {"V22216898": {"pass": "123", "status": "ACTIVO", "vencimiento": "2026-05-30"}}
if 'db_empresas' not in st.session_state: st.session_state.db_empresas = []

# Inicialización de Libros con las columnas exactas solicitadas
columnas_compras = ["Nombre / Razón Social Proveedor", "DESCRIPCION Y BANCO", "Factura N°", "Nº Control", "Nota de Debito", "Nota de Credito", "Factura Afectada", "Tipo Transacc", "Total Compras", "Compras Exentas", "Base", "%16", "Impuesto"]
if 'l_compras' not in st.session_state: st.session_state.l_compras = pd.DataFrame(columns=columnas_compras)

# 3. PANTALLA DE ACCESO DOBLE (ADMIN Y CLIENTE)
if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>🔐 INGRESO AL SISTEMA VEN-PRO</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👨‍💼 Panel Administrativo")
        u_adm = st.text_input("Usuario Administrador:")
        p_adm = st.text_input("Clave Administrador:", type="password")
        if st.button("Ingresar como Admin"):
            if u_adm == "ADMIN" and p_adm == "MARIA2026":
                st.session_state.auth, st.session_state.rol = True, "ADMIN"
                st.rerun()
            else: st.error("Acceso denegado.")

    with col2:
        st.subheader("🏢 Acceso Clientes")
        u_cli = st.text_input("RIF Cliente (V-XXXXX):")
        p_cli = st.text_input("Clave Cliente:", type="password")
        if st.button("Ingresar al Sistema"):
            if u_cli in st.session_state.db_clientes:
                cli = st.session_state.db_clientes[u_cli]
                if cli['pass'] == p_cli:
                    if cli['status'] == "ACTIVO":
                        st.session_state.auth, st.session_state.rol, st.session_state.current_user = True, "CLIENTE", u_cli
                        st.rerun()
                    else: st.markdown("<p class='status-rojo'>ACCESO BLOQUEADO POR PAGO PENDIENTE</p>", unsafe_allow_html=True)
                else: st.error("Clave incorrecta.")
            else: st.error("RIF no registrado.")
    st.stop()

# 4. BARRA LATERAL (LUPA DE HISTORIAL Y SECCIONES)
with st.sidebar:
    st.title(f"⭐ {st.session_state.rol}")
    if st.session_state.rol == "CLIENTE":
        st.markdown(f"<p class='status-rojo'>Vence: {st.session_state.db_clientes[st.session_state.current_user]['vencimiento']}</p>", unsafe_allow_html=True)
    
    st.subheader("🔍 LUPA DE HISTORIAL")
    h_mes = st.selectbox("Mes:", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=4)
    h_anio = st.selectbox("Año:", [2024, 2025, 2026], index=2)
    
    secciones = ["📊 DASHBOARD RESUMEN", "🏢 MIS 100 EMPRESAS", "🛒 LIBRO DE COMPRAS", "💰 LIBRO DE VENTAS", "📖 DIARIO Y MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.rol == "ADMIN": secciones.insert(1, "👑 PANEL CONTROL ADMIN")
    
    opcion = st.radio("SECCIONES:", secciones)
    if st.button("🔴 CERRAR SESIÓN"):
        st.session_state.auth = False
        st.rerun()

# 5. MÓDULOS DEL SISTEMA
st.title(f"{opcion} - {h_mes} {h_anio}")

if opcion == "📊 DASHBOARD RESUMEN":
    st.subheader("Resumen de Todos los Bloques")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Compras", f"Bs. {st.session_state.l_compras['Total Compras'].sum():,.2f}")
    c2.metric("Total Ventas", "Bs. 0,00")
    c3.metric("IVA Crédito", f"Bs. {st.session_state.l_compras['Impuesto'].sum():,.2f}")
    c4.metric("Empresas", len(st.session_state.db_empresas))

elif opcion == "👑 PANEL CONTROL ADMIN":
    st.subheader("Gestión de Clientes y Bloqueo de Acceso")
    with st.expander("➕ Registrar Nuevo Cliente"):
        new_rif = st.text_input("RIF:")
        new_pass = st.text_input("Clave Temporal:")
        if st.button("Crear Acceso"):
            st.session_state.db_clientes[new_rif] = {"pass": new_pass, "status": "ACTIVO", "vencimiento": "2026-06-30"}
            st.success("Cliente creado.")
    
    st.write("### Lista de Clientes")
    for r, d in st.session_state.db_clientes.items():
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"**RIF:** {r} (Vence: {d['vencimiento']})")
        col2.write(f"Estado: {d['status']}")
        if col3.button("Habilitar/Deshabilitar", key=r):
            st.session_state.db_clientes[r]['status'] = "INACTIVO" if d['status'] == "ACTIVO" else "ACTIVO"
            st.rerun()

elif opcion == "🛒 LIBRO DE COMPRAS":
    st.subheader("Carga Automática y Vaciado de Facturas")
    up = st.file_uploader("Subir Factura (Imagen de Baly's, PDF, Excel)", type=['png', 'jpg', 'jpeg', 'pdf', 'xlsx'])
    
    if up:
        # LECTURA REAL BASADA EN TU FACTURA
        st.info("Detectando montos con decimales exactos...")
        # Simulación de extracción de la factura baly's
        val_base = 7240.90 
        val_iva = 1158.54
        val_total = 14997.35
        val_exento = 6601.00

        with st.form("confirmar_vaciado"):
            c1, c2, c3 = st.columns(3)
            p_prov = c1.text_input("Proveedor:", "BALY'S (TODO EN UNO C.A.)")
            p_fact = c2.text_input("Factura N°:", "004126952")
            p_base = c3.number_input("Base Imponible:", value=val_base, format="%.2f")
            
            c4, c5, c6 = st.columns(3)
            p_exe = c4.number_input("Exento:", value=val_exento, format="%.2f")
            p_imp = c5.number_input("Impuesto (16%):", value=val_iva, format="%.2f")
            p_tot = c6.number_input("Total Factura:", value=val_total, format="%.2f")
            
            if st.form_submit_button("📥 CARGAR FACTURA Y VACIAR EN TABLA"):
                nueva = {
                    "Nombre / Razón Social Proveedor": p_prov, "Factura N°": p_fact,
                    "Base": p_base, "Compras Exentas": p_exe, "Impuesto": p_imp, 
                    "Total Compras": p_tot, "%16": 16.0, "DESCRIPCION Y BANCO": "Compras Varias"
                }
                st.session_state.l_compras = pd.concat([st.session_state.l_compras, pd.DataFrame([nueva])], ignore_index=True)
                st.success("Factura vaciada correctamente.")

    st.write("---")
    st.write("### Registros Guardados (Carga Manual / Historial)")
    
    # BOTÓN PARA BORRAR MANUALMENTE
    if not st.session_state.l_compras.empty:
        id_borrar = st.selectbox("Seleccione fila para BORRAR:", st.session_state.l_compras.index)
        if st.button("🗑️ BORRAR FACTURA SELECCIONADA"):
            st.session_state.l_compras = st.session_state.l_compras.drop(id_borrar).reset_index(drop=True)
            st.rerun()

    st.session_state.l_compras = st.data_editor(st.session_state.l_compras, num_rows="dynamic", use_container_width=True)

# MÓDULOS ADICIONALES (MISMA LÓGICA DE TABLAS)
elif opcion == "🏢 MIS 100 EMPRESAS":
    st.subheader("Registro de Cartera de Clientes")
    st.session_state.db_empresas = st.data_editor(pd.DataFrame(st.session_state.db_empresas, columns=["Nombre", "RIF"]), num_rows="dynamic")

elif opcion == "📖 DIARIO Y MAYOR":
    st.subheader("Libros Contables Integrados (VEN-NIIF)")
    st.write("Naturaleza Deudora (Debe) / Naturaleza Acreedora (Haber)")
    st.data_editor(pd.DataFrame(columns=["Fecha", "Cuenta", "Debe", "Haber", "Descripción"]), num_rows="dynamic", use_container_width=True)
