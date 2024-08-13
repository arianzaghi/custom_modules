from odoo import api, fields, models


class PntStockPickingSupplier(models.Model):
    _name = "pnt.stock.picking.supplier"
    _description = "Stock Picking Supplier"
    _check_company_auto = True
    _rec_name = "pnt_name"
    _sql_constraints = [
        (
            "pnt_name_uniq",
            "unique (pnt_name, company_id)",
            "Supplier Picking name must be unique.",
        ),
    ]

    pnt_name = fields.Char(
        string="Supplier Picking Number",
        required=True,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    pnt_supplier_id = fields.Many2one(
        string="Supplier",
        comodel_name="res.partner",
        required=True,
        check_company=True,
        ondelete="cascade",
    )
    pnt_picking_ids = fields.One2many(
        string="Pickings",
        comodel_name="stock.picking",
        inverse_name="pnt_stock_picking_supplier_id",
    )
    pnt_all_invoiced = fields.Boolean(
        string="All Invoiced",
        compute="_compute_pnt_all_invoiced",
        store=True,
    )

    pnt_account_move_loaded_id = fields.Many2one(
        comodel_name='account.move',
        string="Loaded in Account Move",
    )

    pnt_account_move_history_id = fields.Many2one(
        comodel_name='account.move',
        string="History of Account Move",
    )

    @api.depends("pnt_picking_ids.pnt_is_invoiced")
    def _compute_pnt_all_invoiced(self):
        """Compute if all pickings are invoiced."""
        for record in self:
            any_not_invoiced = any(record.pnt_picking_ids.filtered(lambda picking: not picking.pnt_is_invoiced))
            record.pnt_all_invoiced = not any_not_invoiced
