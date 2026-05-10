# 🇻🇪 OmniContable VE - Especificación Técnica

## 🎯 Objetivo del Sistema
Desarrollar una plataforma SaaS multitenant para la gestión contable y fiscal de más de **10,000 empresas**, con automatización OCR y sincronización total bajo **VEN-NIIF**.

---

## 🏗️ 1. Arquitectura y Seguridad
* **Multitenancy:** Administrador global gestiona "Entidades".
* **Control de Acceso:** Login diferenciado con hashing de contraseñas.
* **Interfaz:** 100% en Español con Logout de "Salida Rápida".
* **Gestión de Clientes:** Panel administrativo para habilitar/deshabilitar por pago.

## 🤖 2. Automatización y OCR
* **Pipeline Masivo:** Procesamiento de lotes de hasta 100,000 archivos (PDF/JPG).
* **Sincronización en Cascada:** Actualización automática de Libro Diario, Mayor y Auxiliares.

## ⚖️ 3. Módulos Fiscales (Venezuela)
* **Libros de Compra/Venta:** Manejo de alícuotas (16%, 8%) e IGTF.
* **Ley de Pensiones 2025:** Cálculo del 9% (alícuota editable) sobre base imponible salarial.
* **Alcaldía:** Control de IAE, Inmuebles y Tasas de Aseo.

## 📑 4. Salida de Datos (Formatos SENIAT)
### Formato TXT: IVA
* **Regla:** Separador `|`, decimal con `,`, sin separadores de miles.
* **Ejemplo:** `J500773587|202605|2026-05-09|01|01|V12345678|000125|00-4587|12180,00|10500,00|1680,00|0|0|16|0`

### Formato XML: Retenciones ISLR
```xml
<RelacionRetencionesISLR RifAgente="J500773587" Periodo="202605">
    <DetalleRetencion>
        <RifRetenido>V12345678</RifRetenido>
        <NumeroFactura>000125</NumeroFactura>
        <MontoOperacion>10500,00</MontoOperacion>
        <PorcentajeRetencion>3,00</PorcentajeRetencion>
    </DetalleRetencion>
</RelacionRetencionesISLR>
# 🇻🇪 OmniContable VE - Especificación Técnica

## 🎯 Objetivo del Sistema
Desarrollar una plataforma SaaS multitenant para la gestión contable y fiscal de más de **10,000 empresas**, con automatización OCR y sincronización total bajo **VEN-NIIF**.

---

## 🏗️ 1. Arquitectura y Seguridad
* **Multitenancy:** Administrador global gestiona "Entidades".
* **Control de Acceso:** Login diferenciado con hashing de contraseñas.
* **Interfaz:** 100% en Español con Logout de "Salida Rápida".
* **Gestión de Clientes:** Panel administrativo para habilitar/deshabilitar por pago.

## 🤖 2. Automatización y OCR
* **Pipeline Masivo:** Procesamiento de lotes de hasta 100,000 archivos (PDF/JPG).
* **Sincronización en Cascada:** Actualización automática de Libro Diario, Mayor y Auxiliares.

## ⚖️ 3. Módulos Fiscales (Venezuela)
* **Libros de Compra/Venta:** Manejo de alícuotas (16%, 8%) e IGTF.
* **Ley de Pensiones 2025:** Cálculo del 9% (alícuota editable) sobre base imponible salarial.
* **Alcaldía:** Control de IAE, Inmuebles y Tasas de Aseo.

## 📑 4. Salida de Datos (Formatos SENIAT)
### Formato TXT: IVA
* **Regla:** Separador `|`, decimal con `,`, sin separadores de miles.
* **Ejemplo:** `J500773587|202605|2026-05-09|01|01|V12345678|000125|00-4587|12180,00|10500,00|1680,00|0|0|16|0`

### Formato XML: Retenciones ISLR
```xml
<RelacionRetencionesISLR RifAgente="J500773587" Periodo="202605">
    <DetalleRetencion>
        <RifRetenido>V12345678</RifRetenido>
        <NumeroFactura>000125</NumeroFactura>
        <MontoOperacion>10500,00</MontoOperacion>
        <PorcentajeRetencion>3,00</PorcentajeRetencion>
    </DetalleRetencion>
</RelacionRetencionesISLR>

📈 Ajuste por Inflación (Fórmula Crítica)$$Factor = \frac{INPC_{final}}{INPC_{inicial}}$$El sistema deberá cruzar esta fórmula con la tabla de valores que emita el BCV mensualmente
