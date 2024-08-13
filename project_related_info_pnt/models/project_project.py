from odoo import api, fields, models


class ProjectProject(models.Model):
    _name = "project.project"
    _inherit = ["project.project", "sql.search.mixin"]

    pnt_project_related_info_config_id = fields.Many2one(
        default=lambda self: self.get_default_project_config_id,
        readonly=True,
    )

    pnt_show_sale_orders = fields.Boolean(
        related='pnt_project_related_info_config_id.show_sale_orders',
    )

    @api.model
    def get_default_project_config_id(self):
        return self.env['project.related.info.config'].sudo().search([], limit=1)

    def _has_analytic_account(self):
        self.ensure_one()
        return bool(self.analytic_account_id.id)

    def _get_related_records(self, model, domain, search_field=None):
        self.ensure_one()
        if not self._has_analytic_account():
            return self.env[model]
        if search_field:
            record_ids = self._get_disctinct_ids_with_field(
                model,
                domain,
                search_field,
                self.analytic_account_id.id
            )
            return self.env[model].browse(record_ids)
        return self.env[model].search(domain)

    # -------- SALE ORDERS  -------- #
    def _pnt_get_project_saleorder_ids(self):
        return self._get_related_records('sale.order', [('analytic_account_id.id', '=', self.analytic_account_id.id)])

    pnt_sale_order_count = fields.Integer(
        string='Sale Order Count',
        compute='_compute_pnt_sale_order_count',
        store=False,
    )

    @api.depends('analytic_account_id')
    def _compute_pnt_sale_order_count(self):
        for project in self:
            if not project._has_analytic_account():
                project.pnt_sale_order_count = 0
                continue
            saleorders = project._pnt_get_project_saleorder_ids()
            project.pnt_sale_order_count = len(saleorders)

    def pnt_open_sale_order_ids(self):
        self.ensure_one()
        project_sale_orders = self._pnt_get_project_saleorder_ids()
        return {
            'name': 'Sale Orders',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', project_sale_orders.ids)]
        }

    # -------- SALE INVOICES  -------- #
    def _pnt_get_project_sale_invoice_ids(self):
        move_line_ids = self._get_related_records(
            'account.move.line',
            [('move_type', 'in', ['out_invoice', 'out_refund'])],
            'analytic_distribution'
        )
        return move_line_ids.mapped('move_id')

    pnt_sale_invoice_count = fields.Integer(
        string='Sale Invoice Count',
        compute='_compute_pnt_sale_invoice_count'
    )

    @api.depends('analytic_account_id')
    def _compute_pnt_sale_invoice_count(self):
        for project in self:
            if not project._has_analytic_account():
                project.pnt_sale_invoice_count = 0
                continue
            invoices = project._pnt_get_project_sale_invoice_ids()
            project.pnt_sale_invoice_count = len(invoices)

    def pnt_open_sale_invoice_ids(self):
        self.ensure_one()
        project_sale_invoices = self._pnt_get_project_sale_invoice_ids()
        return {
            'name': 'Sale Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', project_sale_invoices.ids)]
        }

    # -------- PURCHASE ORDERS  -------- #
    def _pnt_get_project_purchaseorder_ids(self):
        order_line_ids = self._get_related_records(
            'purchase.order.line',
            [],
            'analytic_distribution'
        )
        return order_line_ids.mapped('order_id')

    pnt_purchase_order_count = fields.Integer(
        string='Purchase Order Count',
        compute='_compute_pnt_purchase_order_count'
    )

    @api.depends('analytic_account_id')
    def _compute_pnt_purchase_order_count(self):
        for project in self:
            if not project._has_analytic_account():
                project.pnt_purchase_order_count = 0
                continue
            purchase_orders = project._pnt_get_project_purchaseorder_ids()
            project.pnt_purchase_order_count = len(purchase_orders)

    def pnt_open_purchase_order_ids(self):
        self.ensure_one()
        project_purchase_orders = self._pnt_get_project_purchaseorder_ids()
        return {
            'name': 'Purchase Orders',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', project_purchase_orders.ids)]
        }

    # -------- PURCHASE INVOICES  -------- #
    def _pnt_get_project_purchase_invoice_ids(self):
        move_line_ids = self._get_related_records(
            'account.move.line',
            [('move_type', 'in', ['in_invoice', 'in_refund'])],
            'analytic_distribution'
        )
        return move_line_ids.mapped('move_id')

    pnt_purchase_invoice_count = fields.Integer(
        string='Purchase Invoice Count',
        compute='_compute_pnt_purchase_invoice_count'
    )

    @api.depends('analytic_account_id')
    def _compute_pnt_purchase_invoice_count(self):
        for project in self:
            if not project._has_analytic_account():
                project.pnt_purchase_invoice_count = 0
                continue
            purchase_invoices = project._pnt_get_project_purchase_invoice_ids()
            project.pnt_purchase_invoice_count = len(purchase_invoices)

    def pnt_open_purchase_invoice_ids(self):
        self.ensure_one()
        project_purchase_invoices = self._pnt_get_project_purchase_invoice_ids()
        return {
            'name': 'Purchase Invoices',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', project_purchase_invoices.ids)]
        }

    # -------- OUTGOING PICKINGS  -------- #
    def _pnt_get_outgoing_pickings(self):
        self.ensure_one()
        if not self._has_analytic_account():
            return self.env['stock.picking']
        sale_orders = self._pnt_get_project_saleorder_ids()
        outgoing_picking_lines = self.env['stock.move'].search([
            ('sale_line_id.order_id', 'in', sale_orders.ids)
        ])
        return outgoing_picking_lines.mapped('picking_id')

    pnt_outgoing_picking_count = fields.Integer(
        string='Outgoing Picking Count',
        compute='_compute_pnt_outgoing_picking_count'
    )

    @api.depends('analytic_account_id')
    def _compute_pnt_outgoing_picking_count(self):
        for project in self:
            if not project._has_analytic_account():
                project.pnt_outgoing_picking_count = 0
                continue
            outgoing_pickings = project._pnt_get_outgoing_pickings()
            project.pnt_outgoing_picking_count = len(outgoing_pickings)

    def pnt_open_outgoing_picking_ids(self):
        self.ensure_one()
        outgoing_pickings = self._pnt_get_outgoing_pickings()
        return {
            'name': 'Outgoing Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', outgoing_pickings.ids)]
        }

    # -------- INCOMING PICKINGS  -------- #
    def _pnt_get_incoming_pickings(self):
        self.ensure_one()
        if not self._has_analytic_account():
            return self.env['stock.picking']
        purchase_orders = self._pnt_get_project_purchaseorder_ids()
        incoming_picking_lines = self.env['stock.move'].search([
            ('purchase_line_id.order_id', 'in', purchase_orders.ids)
        ])
        return incoming_picking_lines.mapped('picking_id')

    pnt_incoming_picking_count = fields.Integer(
        string='Incoming Picking Count',
        compute='_compute_pnt_incoming_picking_count'
    )

    @api.depends('analytic_account_id')
    def _compute_pnt_incoming_picking_count(self):
        for project in self:
            if not project._has_analytic_account():
                project.pnt_incoming_picking_count = 0
                continue
            incoming_pickings = project._pnt_get_incoming_pickings()
            project.pnt_incoming_picking_count = len(incoming_pickings)

    def pnt_open_incoming_picking_ids(self):
        self.ensure_one()
        incoming_pickings = self._pnt_get_incoming_pickings()
        return {
            'name': 'Incoming Pickings',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', incoming_pickings.ids)]
        }

    # -------- PRODUCTION ORDERS  -------- #
    def _pnt_get_production_orders(self):
        self.ensure_one()
        if not self._has_analytic_account():
            return self.env['mrp.production']
        production_orders = self.env['mrp.production'].search([
            ('analytic_distribution', '!=', False)
        ]).filtered(lambda prod: str(self.analytic_account_id.id) in prod.analytic_distribution)
        return production_orders

    pnt_production_order_count = fields.Integer(
        string='Production Order Count',
        compute='_compute_pnt_production_order_count'
    )

    @api.depends('analytic_account_id')
    def _compute_pnt_production_order_count(self):
        for project in self:
            if not project._has_analytic_account():
                project.pnt_production_order_count = 0
                continue
            production_orders = project._pnt_get_production_orders()
            project.pnt_production_order_count = len(production_orders)

    def pnt_open_production_order_ids(self):
        self.ensure_one()
        production_orders = self._pnt_get_production_orders()
        return {
            'name': 'Production Orders',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', production_orders.ids)]
        }
