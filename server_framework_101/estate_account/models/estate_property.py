from odoo import models, Command


class EstateProperty(models.Model):
    _name = 'estate.property'
    _inherit = ["estate.property"]

    def action_sell_property(self):
        self.env["account.move"].sudo().with_context(
            default_move_type="out_invoice"
        ).create(
            {
                "partner_id": self.env.user.id,
                "line_ids": [
                    Command.create(
                        {
                            "name": "Commission",
                            "quantity": 1,
                            "price_unit": self.selling_price * 0.06,
                        }
                    ),
                    Command.create(
                        {
                            "name": "Administrative Fees",
                            "quantity": 1,
                            "price_unit": 100,
                        }
                    ),
                ],
            }
        )

        return super().action_sell_property()
