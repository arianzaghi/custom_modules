from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    pnt_stock_picking_supplier_id = fields.Many2one(
        string="Picking Supplier Code",
        comodel_name="pnt.stock.picking.supplier",
        check_company=True,
        compute="_compute_pnt_stock_picking_supplier_id",
        readonly=False,
        store=True,
        copy=False,
    )

    pnt_enable_picking_invoice = fields.Boolean(
        string="Enable Picking Invoice",
        related="picking_type_id.pnt_enable_picking_invoice",
    )

    pnt_is_invoiced = fields.Boolean(
        string="Picking invoiced"
    )

    @api.depends("partner_id")
    def _compute_pnt_stock_picking_supplier_id(self):
        self.pnt_stock_picking_supplier_id = False

    @api.constrains('pnt_stock_picking_supplier_id')
    def _check_unique_supplier_id(self):
        for record in self:
            existing_registry = self.search([
                ('pnt_stock_picking_supplier_id', '=', record.pnt_stock_picking_supplier_id.id),
                ('pnt_stock_picking_supplier_id', '!=', False),
                ('id', '!=', record.id)
            ])
            if existing_registry:
                raise ValidationError(_("This picking supplier id has already been used"))
