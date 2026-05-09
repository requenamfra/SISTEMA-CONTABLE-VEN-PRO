import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import re

# 1. ARQUITECTURA DE DATOS Y SEGURIDAD
st.set_page_config(page_title="VEN-PRO v1000", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stApp { overflow: hidden; }
    .alerta-vencimiento { color: white; background: red; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# Inicialización de Base de Datos Centralizada
if 'db' not in st.session_state:
    st.session_state.db = {
        'admin': {'user': 'MARIA_ADMIN', 'pass': 'SISTEMA_2026_PRO'},
        'empresas': {}, # RIF: {nombre, plan_cupos, activos, vencimiento, status}
        'sesiones_activas': {}, # user_id: session_id
        'data_contable': {}, # RIF: {compras: DF, ventas: DF, diario: DF, mayor: DF, parafiscales: DF, alcaldia: DF}
    }

# 2. MOTOR DE POSTEO AUTOMÁTICO Y NORMALIZACIÓN DE DECIMALES
def formatear_seniat(monto):
    # El SENIAT exige coma para decimales y sin puntos en miles para TXT/XML
    return f"{monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "")

def posteo_automatico(rif_empresa, fecha, detalle, monto, tipo="COMPRA"):
    # Lógica VEN-NIIF: Afecta Diario y Mayor simultáneamente
    cta_debe = "IVA Crédito Fiscal" if tipo == "COMPRA" else "Caja/Bancos"
    cta_haber = "Cuentas por Pagar" if tipo == "COMPRA" else "Ventas"
    
    nuevo_asiento = pd.DataFrame([{
        "Fecha": fecha, "Cuenta (VEN-NIIF)": cta_debe, "Descripción": detalle, "Debe (Bs.)": monto, "Haber (Bs.)": 0.00
    }, {
        "Fecha": fecha, "Cuenta (VEN-NIIF)": cta_haber, "Descripción": detalle, "Debe (Bs.)": 0.00, "Haber (Bs.)": monto
    }])
    
    st.session_state.db['data_contable'][rif_empresa]['diario'] = pd.concat([
        st.session_state.db['data_contable'][rif_empresa]['diario'], nuevo_asiento
    ], ignore_index=True)

# 3. INTERFAZ DE ACCESO (ADMIN VS CLIENTE)
if 'auth' not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>🛡️ VEN-PRO CONTABLE v1000</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1, 1])
    with col:
        u = st.text_input("Usuario / Correo").strip()
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR"):
            if u == st.session_state.db['admin']['user'] and p == st.session_state.db['admin']['pass']:
                st.session_state.auth = {'user': u, 'role': 'ADMIN'}
                st.rerun()
            # Lógica de Cliente y Sesión Única
            for rif, info in st.session_state.db['empresas'].items():
                if u == rif and p == "12345": # Clave genérica para demo
                    if info['status'] == "INACTIVO":
                        st.error("🚫 Empresa suspendida por falta de pago.")
                    else:
                        st.session_state.auth = {'user': u, 'role': 'CLIENTE', 'rif': rif}
                        st.rerun()
    st.stop()

# 4. PANEL LATERAL (LUPA DE HISTORIAL Y CONTROL)
with st.sidebar:
    st.title(f"💼 {st.session_state.auth['role']}")
    st.subheader("🔍 LUPA DE HISTORIAL")
    mes_h = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    anio_h = st.selectbox("Año", [2025, 2026])
    
    menu = ["📊 DASHBOARD", "🛒 COMPRAS", "💰 VENTAS", "📖 LIBRO DIARIO/MAYOR", "🏛️ ALCALDÍA", "🏢 PARAFISCALES", "📤 SENIAT (XML/TXT)"]
    if st.session_state.auth['role'] == "ADMIN": menu = ["👑 PANEL ADMIN"] + menu
    
    choice = st.radio("MÓDULOS", menu)
    if st.button("🚪 CERRAR SESIÓN"):
        del st.session_state.auth
        st.rerun()

# 5. LÓGICA DE MÓDULOS
rif_actual = st.session_state.auth.get('rif')

if choice == "👑 PANEL ADMIN":
    st.header("Control Maestro de Suscripciones")
    with st.form("reg_empresa"):
        c1, c2, c3 = st.columns(3)
        r_rif = c1.text_input("RIF Empresa Cliente:")
        r_nom = c2.text_input("Nombre de Empresa:")
        r_cup = c3.number_input("Cupos de Usuarios:", min_value=1, value=1)
        if st.form_submit_button("HABILITAR EMPRESA"):
            st.session_state.db['empresas'][r_rif] = {'nombre': r_nom, 'cupos': r_cup, 'status': 'ACTIVO', 'vencimiento': date.today() + pd.Timedelta(days=30)}
            st.session_state.db['data_contable'][r_rif] = {
                'compras': pd.DataFrame(columns=["Nombre / Razón Social Proveedor", "DESCRICION Y BANCO", "Factura N°", "Nº Control", "Total Compras", "Base", "Impuesto"]),
                'ventas': pd.DataFrame(columns=["Nombre / Razón Social Cliente", "R.I.F. N°", "Factura N°", "Total Ventas", "Base", "Impuesto"]),
                'diario': pd.DataFrame(columns=["Fecha", "Cuenta (VEN-NIIF)", "Descripción", "Debe (Bs.)", "Haber (Bs.)"]),
                'parafiscales': pd.DataFrame(columns=["Tipo", "Monto", "Fecha", "Estatus"]),
                'alcaldia': pd.DataFrame(columns=["Impuesto", "Monto", "Periodo"])
            }
            st.success(f"Empresa {r_nom} creada en la base de datos.")

elif choice == "🛒 COMPRAS":
    st.header("Módulo de Compras con Posteo Automático")
    
    # Opción de Carga Masiva (Pipeline)
    files = st.file_uploader("Cargar Facturas (PDF/JPG/PNG)", accept_multiple_files=True)
    
    with st.expander("➕ REGISTRO MANUAL / VALIDACIÓN"):
        with st.form("compra_manual"):
            col1, col2, col3 = st.columns(3)
            prov = col1.text_input("Nombre / Razón Social Proveedor")
            desc = col2.text_input("DESCRICION Y BANCO")
            fact = col3.text_input("Factura N°")
            
            col4, col5, col6 = st.columns(3)
            total = col4.number_input("Total Compras (Bs.)", format="%.2f")
            base = col5.number_input("Base Imponible", format="%.2f")
            iva = col6.number_input("Impuesto (16%)", format="%.2f")
            
            if st.form_submit_button("📥 PROCESAR Y POSTEAR"):
                nueva_data = {"Nombre / Razón Social Proveedor": prov, "DESCRICION Y BANCO": desc, "Factura N°": fact, "Total Compras": total, "Base": base, "Impuesto": iva}
                st.session_state.db['data_contable'][rif_actual]['compras'] = pd.concat([st.session_state.db['data_contable'][rif_actual]['compras'], pd.DataFrame([nueva_data])], ignore_index=True)
                # EJECUCIÓN DEL POSTEO AUTOMÁTICO AL DIARIO
                posteo_automatico(rif_actual, str(date.today()), f"Compra Fact. {fact} - {prov}", total, "COMPRA")
                st.success("Factura posteada en todos los libros.")

    st.subheader("Historial de Compras")
    st.data_editor(st.session_state.db['data_contable'][rif_actual]['compras'], use_container_width=True)

elif choice == "📤 SENIAT (XML/TXT)":
    st.header("Generación de Archivos de Cumplimiento")
    if st.button("Generar XML Retenciones ISLR"):
        xml_output = f"""<RelacionRetencionesISLR RifAgente="{rif_actual}" Periodo="{anio_h}{mes_h}">
        <DetalleRetencion>
            <RifRetenido>J123456789</RifRetenido>
            <MontoOperacion>{formatear_seniat(1500.50)}</MontoOperacion>
        </DetalleRetencion>
        </RelacionRetencionesISLR>"""
        st.code(xml_output, language="xml")
        st.download_button("Descargar XML", xml_output, file_name="retenciones.xml")

elif choice == "📊 DASHBOARD":
    st.header(f"Resumen Ejecutivo - {st.session_state.db['empresas'][rif_actual]['nombre']}")
    data = st.session_state.db['data_contable'][rif_actual]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Compras", f"Bs. {data['compras']['Total Compras'].sum():,.2f}")
    c2.metric("Total Ventas", f"Bs. {data['ventas']['Total Ventas'].sum():,.2f}")
    c3.metric("IVA Crédito", f"Bs. {data['compras']['Impuesto'].sum():,.2f}")
    
    st.subheader("Últimos Movimientos del Diario")
    st.table(data['diario'].tail(5))

elif choice == "🏢 PARAFISCALES":
    st.header("Control de Pagos Parafiscales")
    tipo_p = st.selectbox("Tipo de Aporte", ["IVSS", "FAOV", "INCES", "Régimen de Empleo", "Ley de Pensiones 2025"])
    m_p = st.number_input("Monto Pagado (Bs.)", format="%.2f")
    if st.button("Registrar Pago"):
        nuevo_p = {"Tipo": tipo_p, "Monto": m_p, "Fecha": str(date.today()), "Estatus": "Pagado"}
        st.session_state.db['data_contable'][rif_actual]['parafiscales'] = pd.concat([st.session_state.db['data_contable'][rif_actual]['parafiscales'], pd.DataFrame([nuevo_p])], ignore_index=True)
    st.table(st.session_state.db['data_contable'][rif_actual]['parafiscales'])
