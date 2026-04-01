from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = "account.payment"

    counterpart_account_id = fields.Many2one(
        "account.account",
        string="Cuenta Contrapartida",
        domain="[('deprecated','=',False)]",
    )

    @api.model
    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        lines = super()._prepare_move_line_default_vals(write_off_line_vals)

        for line in lines:
            # Detecta la línea de contrapartida (normalmente payable/receivable)
            if line.get("account_id") == self.destination_account_id.id:

                if self.counterpart_account_id:
                    line["account_id"] = self.counterpart_account_id.id

        return lines
