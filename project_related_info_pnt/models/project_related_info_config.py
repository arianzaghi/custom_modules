from odoo import models, fields


class ProjectRelatedInfoConfig(models.Model):
    _name = 'project.related.info.config'
    _description = 'Customizes buttons shown on project info'

    show_sale_orders = fields.Boolean(string='Show Sale Orders', default=True)
    show_sale_invoices = fields.Boolean(string='Show Sale Invoices', default=True)
    show_purchase_orders = fields.Boolean(string='Show Purchase Orders', default=True)
    show_purchase_invoices = fields.Boolean(string='Show Purchase Invoices', default=True)
    show_outgoing_pickings = fields.Boolean(string='Show Outgoing Pickings', default=True)
    show_incoming_pickings = fields.Boolean(string='Show Incoming Pickings', default=True)
    show_production_orders = fields.Boolean(string='Show Production Orders', default=True)

