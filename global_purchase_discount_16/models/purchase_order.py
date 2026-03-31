# -*- coding: utf-8 -*-
"""
Global Purchase Discount - Odoo 16 Community
=============================================
Añade el campo 'Global Discount (%)' a purchase.order y purchase.order.line.

Diferencias respecto a la versión 18:
- En Odoo 16 Community NO existe el widget 'account-tax-totals-field' en compras,
  por lo que los totales se muestran con campos Monetary independientes.
- create() usa @api.model_create_multi (disponible desde v13).
- El campo discount en purchase.order.line NO existe por defecto en Odoo 16;
  se agrega aquí y se calcula price_subtotal sobreescribiendo el método.
- Se usa _amount_all() heredado para recalcular amount_untaxed y amount_total
  incluyendo el descuento global.
"""

from odoo import api, fields, models, _
from odoo.tools import float_round


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # En Odoo 16 Community, purchase.order.line NO tiene campo discount nativo.
    # Lo agregamos aquí para poder aplicar el descuento global por línea.
    discount = fields.Float(
        string='Disc.%',
        digits='Discount',
        default=0.0,
    )

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        """
        Sobreescribe el cálculo estándar para incluir el descuento por línea.
        En Odoo 16 el método se llama _compute_amount y actualiza price_subtotal
        y price_total.
        """
        for line in self:
            # Precio con descuento aplicado
            price = line.price_unit * (1.0 - line.discount / 100.0)
            taxes = line.taxes_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.update({
                'price_tax': sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', [])
                ),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # ── Campos nuevos ────────────────────────────────────────────────────────

    global_discount = fields.Float(
        string='Global Discount (%)',
        default=0.0,
        digits='Discount',
        tracking=True,
    )

    # Monto bruto SIN descuento (suma de precio_unit * qty de cada línea)
    total_amount_untaxed = fields.Monetary(
        string='Untaxed Amount',
        store=True,
        readonly=True,
        compute='_compute_global_discount_totals',
        currency_field='currency_id',
        help='Subtotal antes de aplicar el descuento global.',
    )

    # Importe total del descuento (positivo, para mostrar)
    total_discount_amount = fields.Monetary(
        string='Discount',
        store=True,
        readonly=True,
        compute='_compute_global_discount_totals',
        currency_field='currency_id',
    )

    # Importe total del descuento (negativo, para mostrar con signo)
    total_discount_amount_display = fields.Monetary(
        string='Discount',
        store=True,
        readonly=True,
        compute='_compute_global_discount_totals',
        currency_field='currency_id',
    )

    # ── Cómputos ─────────────────────────────────────────────────────────────

    @api.depends(
        'order_line.price_unit',
        'order_line.product_qty',
        'order_line.discount',
        'global_discount',
    )
    def _compute_global_discount_totals(self):
        """
        Calcula:
          - total_amount_untaxed : suma bruta (sin descuento)
          - total_discount_amount : importe descontado (positivo)
          - total_discount_amount_display : importe descontado (negativo, para mostrar)
        """
        for order in self:
            gross_total = 0.0
            discount_total = 0.0
            for line in order.order_line:
                line_gross = line.price_unit * line.product_qty
                line_discount = line_gross * (line.discount / 100.0)
                gross_total += line_gross
                discount_total += line_discount

            order.total_amount_untaxed = gross_total
            order.total_discount_amount = discount_total
            order.total_discount_amount_display = -discount_total

    # ── Override create/write para propagar el descuento a las líneas ────────

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.global_discount:
                order.order_line.write({'discount': order.global_discount})
        return orders

    def write(self, vals):
        result = super().write(vals)
        if 'global_discount' in vals:
            for order in self:
                order.order_line.write({'discount': order.global_discount})
        return result
