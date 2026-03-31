# Global Purchase Discount — Odoo 16 Community

## Descripción
Módulo que permite aplicar un **descuento global (%)** sobre todas las líneas de
una **Solicitud de Cotización (RFQ)** o una **Orden de Compra (PO)** en Odoo 16 Community.

## Características
- Campo **Global Discount (%)** en el formulario de compras (RFQ y PO).
- El descuento se propaga automáticamente a todas las líneas al guardar.
- Columna **Disc.%** visible en la tabla de líneas.
- Totales desglosados en el formulario:
  - Untaxed Amount (bruto)
  - Discount (negativo)
  - Discounted Amount
  - Tax
  - **Total**
- Reporte PDF (Print RFQ / Print Purchase Order) actualizado con el mismo desglose.
- Traducción al español incluida.

## Instalación
1. Copiar la carpeta `global_purchase_discount` al directorio de addons de Odoo.
2. Reiniciar el servicio Odoo.
3. Activar el módulo desde **Ajustes → Apps → Global Purchase Discount**.

```bash
# Ejemplo Ubuntu
sudo cp -r global_purchase_discount /opt/odoo/custom-addons/
sudo systemctl restart odoo
```

4. Actualizar la lista de apps y buscar **Global Purchase Discount**.

## Compatibilidad
| Versión Odoo | Estado |
|---|---|
| 16.0 Community | ✅ Compatible |
| 16.0 Enterprise | ✅ Compatible |
| 18.0 | Original (módulo fuente) |

## Notas técnicas
- En Odoo 16 Community `purchase.order.line` **no tiene** el campo `discount` nativo,
  por lo que este módulo lo agrega con el tipo `Float` (precisión `Discount`).
- Se sobreescribe `_compute_amount` en `purchase.order.line` para incluir el descuento.
- Los totales se calculan en `_compute_global_discount_totals` sobre `purchase.order`.
- Se usa `@api.model_create_multi` (disponible desde Odoo 13+).
- El widget `account-tax-totals-field` **no está disponible** en el módulo `purchase`
  de Odoo 16 Community; los totales se muestran con campos `Monetary` independientes.
