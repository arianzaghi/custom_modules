from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    class ResConfigSettings(models.TransientModel):
        _inherit = 'res.config.settings'

        show_sale_orders = fields.Boolean(
            related='project_related_info_id.show_sale_orders',
            string='Show Sale Orders',
            readonly=False,
            store=True
        )

        show_sale_invoices = fields.Boolean(
            related='project_related_info_id.show_sale_invoices',
            string='Show Sale Invoices',
            readonly=False,
            store=True
        )

        show_purchase_orders = fields.Boolean(
            related='project_related_info_id.show_purchase_orders',
            string='Show Purchase Orders',
            readonly=False,
            store=True
        )

        show_purchase_invoices = fields.Boolean(
            related='project_related_info_id.show_purchase_invoices',
            string='Show Purchase Invoices',
            readonly=False,
            store=True
        )

        show_outgoing_pickings = fields.Boolean(
            related='project_related_info_id.show_outgoing_pickings',
            string='Show Outgoing Pickings',
            readonly=False,
            store=True
        )

        show_incoming_pickings = fields.Boolean(
            related='project_related_info_id.show_incoming_pickings',
            string='Show Incoming Pickings',
            readonly=False,
            store=True
        )

        show_production_orders = fields.Boolean(
            related='project_related_info_id.show_production_orders',
            string='Show Production Orders',
            readonly=False,
            store=True
        )

        project_related_info_id = fields.Many2one(
            'project.related.info.config',
            string='Project Button Configuration'
        )
