import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date

# 1. CONFIGURACIÓN Y SEGURIDAD
st.set_page_config(page_title="OmniContable VE", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = {
        'usuarios': {'admin@omni.com': {'pass': 'admin123', 'rol': 'ADMIN'}},
        'empresas': {}, # RIF: {nombre, suscripcion, usuarios_adicionales: []}
        'inpc': {'2026-03': 1310.5, '2026-04': 1345.2}, # Tabla BCV
        'contabilidad': {} # RIF: {diario: DF, mayor: DF, facturas: DF}
    }

# 2. FUNCIONES TÉCNICAS CRÍTICAS (SENIAT)
def formato_txt_seniat(valor):
    """Regla de Oro: Coma decimal, sin puntos en miles."""
    return f"{valor:.2f}".replace(".", ",")

def calcular_ajuste_inflacion(valor_historico, mes_inicio, mes_final):
    factor = st.session_state.db['inpc'][mes_final] / st.session_state.db['inpc'][mes_inicio]
    return valor_historico * factor

# 3. INTERFAZ DE LOGÍN
if 'user' not in st.session_state:
    st.title("🛡️ OmniContable VE - Acceso")
    with st.form("login"):
        u = st.text_input("Correo Electrónico")
        p = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Ingresar"):
            if u in st.session_state.db['usuarios'] and st.session_state.db['usuarios'][u]['pass'] == p:
                st.session_state.user = u
                st.session_state.rol = st.session_state.db['usuarios'][u]['rol']
                st.rerun()
    st.stop()

# --- PANEL DE ADMINISTRADOR ---
if st.session_state.rol == "ADMIN":
    st.sidebar.title("👑 MODO ADMINISTRADOR")
    tab_admin = st.tabs(["Gestión de Clientes", "Suscripciones", "Auditoría Global"])
    
    with tab_admin[0]:
        st.subheader("Crear Nueva Empresa y Usuarios")
        with st.form("nueva_empresa"):
            c1, c2, c3 = st.columns(3)
            rif = c1.text_input("RIF Empresa (Ej: J500773587)")
            nom = c2.text_input("Razón Social")
            plan = c3.selectbox("Plan", ["Básico (1 usuario)", "Pro (5 usuarios)", "Enterprise"])
            
            u_cli = st.text_input("Email del Cliente Principal")
            p_cli = st.text_input("Clave de Acceso")
            
            if st.form_submit_button("Registrar Empresa"):
                st.session_state.db['empresas'][rif] = {'nombre': nom, 'plan': plan, 'vence': '2027-01-01'}
                st.session_state.db['usuarios'][u_cli] = {'pass': p_cli, 'rol': 'CLIENTE', 'rif': rif}
                st.success(f"Empresa {nom} creada con éxito.")

# --- PANEL DE CLIENTE / CONTADOR ---
else:
    rif_actual = st.session_state.db['usuarios'][st.session_state.user]['rif']
    st.sidebar.title(f"🏢 {st.session_state.db['empresas'][rif_actual]['nombre']}")
    opcion = st.sidebar.radio("Módulos", ["Dashboard", "Lupa de Historial", "Estado de Resultados", "Ajuste Inflación", "Exportar SENIAT"])

    if opcion == "Lupa de Historial":
        st.header("🔍 Lupa de Historial (Big Data)")
        st.info("Buscador de alta velocidad para 100,000+ registros.")
        
        filtro = st.text_input("Buscar por Factura N°, RIF o Proveedor")
        # Aquí corregimos el error de la imagen anterior (num_rows era el problema)
        st.data_editor(
            pd.DataFrame(columns=["Fecha", "Entidad", "Monto Bs.", "N° Planilla", "Estado"]), 
            num_rows="dynamic",
            use_container_width=True
        )

    elif opcion == "Estado de Resultados":
        st.header("📊 Ganancias y Pérdidas (Comparativa Divisas)")
        tasa = st.number_input("Tasa BCV Referencial (Bs./USD)", value=36.50)
        
        # Datos simulados sincronizados
        data_egp = {
            'Cuenta': ['Ventas Netas', 'Costos de Venta', 'Gastos de Personal', 'Utilidad'],
            'Bs.': [150000.00, -80000.00, -20000.00, 50000.00]
        }
        df_egp = pd.DataFrame(data_egp)
        df_egp['USD (Equiv.)'] = df_egp['Bs.'] / tasa
        
        st.table(df_egp.style.format({'Bs.': '{:,.2f}', 'USD (Equiv.)': '{:,.2f}'}))

    elif opcion == "Ajuste Inflación":
        st.header("📈 Ajuste por Inflación Fiscal (V-NIIF)")
        st.write("Cálculo basado en variaciones del INPC")
        val_h = st.number_input("Valor Histórico del Activo (Bs.)", value=1000.0)
        mes_i = st.selectbox("Mes Inicio", list(st.session_state.db['inpc'].keys()))
        mes_f = st.selectbox("Mes Cierre", list(st.session_state.db['inpc'].keys()))
        
        if st.button("Calcular Reexpresión"):
            reexpresado = calcular_ajuste_inflacion(val_h, mes_i, mes_f)
            st.metric("Valor Reexpresado", f"Bs. {reexpresado:,.2f}", f"Incremento: {reexpresado-val_h:,.2f}")

    elif opcion == "Exportar SENIAT":
        st.header("📤 Generación de Archivos Legales")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Formato TXT IVA")
            ejemplo_txt = f"{rif_actual}|202605|09/05/2026|01|004126952|{formato_txt_seniat(7240.90)}|{formato_txt_seniat(1158.54)}"
            st.code(ejemplo_txt, language="text")
            st.download_button("Descargar TXT", ejemplo_txt)
            
        with col2:
            st.subheader("Formato XML ISLR")
            xml_tpl = f"""<RelacionRetencionesISLR RifAgente="{rif_actual}" Periodo="202605">
<DetalleRetencion>
    <RifRetenido>V12345678</RifRetenido>
    <NumeroFactura>004126952</NumeroFactura>
    <MontoOperacion>{formatear_seniat(7240.90)}</MontoOperacion>
</DetalleRetencion>
</RelacionRetencionesISLR>"""
            st.code(xml_tpl, language="xml")

if st.sidebar.button("Cerrar Sesión"):
    del st.session_state.user
    st.rerun()
