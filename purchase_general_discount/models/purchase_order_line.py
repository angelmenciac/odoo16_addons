from odoo import models, fields, api


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount = fields.Float(
        string="Descuento (%)",
        digits="Discount",
        default=0.0,
    )

    @api.depends("product_qty", "price_unit", "taxes_id", "discount")
    def _compute_amount(self):
        for line in self:
            price_unit_discounted = line.price_unit * (1 - line.discount / 100)

            taxes = line.taxes_id.compute_all(
                price_unit_discounted,
                line.order_id.currency_id,
                line.product_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )

            line.price_subtotal = taxes["total_excluded"]
            line.price_total = taxes["total_included"]
            line.price_tax = line.price_total - line.price_subtotal
