<RelacionRetencionesISLR RifAgente="J500773587" Periodo="202605">
    <DetalleRetencion>
        <RifRetenido>V12345678</RifRetenido>
        <NumeroFactura>000125</NumeroFactura>
        <NumeroControl>00-4587</NumeroControl>
        <MontoOperacion>10500,00</MontoOperacion>
        <CodigoConcepto>001</CodigoConcepto>
        <PorcentajeRetencion>3,00</PorcentajeRetencion>
    </DetalleRetencion>
</RelacionRetencionesISLR>
2. Formato TXT: IVA SENIATRegla: Separador |, decimal con ,, sin miles.J500773587|202605|2026-05-09|01|01|V12345678|000125|00-4587|12180,00|10500,00|1680,00|0|0|16|03. Ajuste por Inflación (INPC)El sistema debe consultar la tabla de st.session_state.inpc (que el programador debe alimentar mensualmente) para aplicar la fórmula:$$Factor = \frac{INPC_{final}}{INPC_{inicial}}$$
