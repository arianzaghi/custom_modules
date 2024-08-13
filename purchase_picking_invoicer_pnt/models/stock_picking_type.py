from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    pnt_enable_picking_invoice = fields.Boolean(
        string="Enable Picking Invoice",
    )

    enable_returns_in_invoice = fields.Boolean(
        string="Include returns in invoices", default=False
    )
