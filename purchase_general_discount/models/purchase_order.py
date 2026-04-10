from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    discount_type = fields.Selection(
        [
            ("percent", "Porcentaje"),
            ("fixed", "Monto fijo"),
        ],
        default="percent",
        string="Tipo de Descuento",
    )

    discount_scope = fields.Selection(
        [
            ("before_tax", "Antes de impuestos"),
            ("after_tax", "Después de impuestos"),
        ],
        default="before_tax",
        string="Aplicación",
    )

    general_discount = fields.Float(string="Descuento")

    discount_amount = fields.Monetary(
        string="Monto Descuento",
        compute="_compute_discount_amount",
        store=True,
        currency_field="currency_id",
    )

    # -----------------------------------
    # COMPUTE MONTO DESCUENTO
    # -----------------------------------
    @api.depends(
        "order_line.price_subtotal",
        "order_line.price_total",
        "general_discount",
        "discount_type",
        "discount_scope",
    )
    def _compute_discount_amount(self):
        for order in self:

            if order.discount_scope == "before_tax":
                base = sum(l.price_subtotal for l in order.order_line)
            else:
                base = sum(l.price_total for l in order.order_line)

            if order.discount_type == "percent":
                discount = base * (order.general_discount / 100)
            else:
                discount = order.general_discount

            order.discount_amount = discount

    # -----------------------------------
    # ONCHANGE
    # -----------------------------------
    @api.onchange("general_discount", "discount_type")
    def _onchange_discount(self):
        for order in self:
            if order.discount_type == "percent":
                for line in order.order_line:
                    line.discount = order.general_discount

    # -----------------------------------
    # DISTRIBUCIÓN MONTO FIJO
    # -----------------------------------
    def _apply_fixed_discount(self):
        for order in self:

            total = sum(l.price_subtotal for l in order.order_line)

            if not total:
                continue

            for line in order.order_line:
                ratio = line.price_subtotal / total
                discount_amount = order.general_discount * ratio

                discount_percent = (
                    (discount_amount / line.price_subtotal) * 100
                    if line.price_subtotal
                    else 0
                )

                line.discount = discount_percent

    # -----------------------------------
    # CREATE / WRITE
    # -----------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            order._apply_discount_logic()
        return orders

    def write(self, vals):
        res = super().write(vals)
        for order in self:
            order._apply_discount_logic()
        return res

    def _apply_discount_logic(self):
        for order in self:
            if order.discount_type == "percent":
                for line in order.order_line:
                    line.discount = order.general_discount
            else:
                order._apply_fixed_discount()

    # -----------------------------------
    # TOTALES
    # -----------------------------------
    @api.depends("order_line.price_subtotal", "order_line.price_tax")
    def _amount_all(self):
        for order in self:
            order.amount_untaxed = sum(l.price_subtotal for l in order.order_line)
            order.amount_tax = sum(l.price_tax for l in order.order_line)
            order.amount_total = order.amount_untaxed + order.amount_tax

    # -----------------------------------
    # FACTURA
    # -----------------------------------
    def _prepare_account_move_line(self, line):
        res = super()._prepare_account_move_line(line)
        res["discount"] = line.discount
        return res
