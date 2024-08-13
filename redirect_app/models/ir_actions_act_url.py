from odoo import models, fields, api


class IrActionsActUrl(models.Model):
    _inherit = 'ir.actions.act_url'

    @api.model
    def create(self, vals):
        if vals.get('url') == '%(redirect_url)d':
            vals['url'] = self.env['ir.config_parameter'].sudo().get_param('pnt.redirect.url', default='https://vda10-2020.sek.net/erpsek-master/')
        return super(IrActionsActUrl, self).create(vals)

    def write(self, vals):
        if vals.get('url') == '%(redirect_url)d':
            vals['url'] = self.env['ir.config_parameter'].sudo().get_param('pnt.redirect.url', default='https://vda10-2020.sek.net/erpsek-master/')
        return super(IrActionsActUrl, self).write(vals)
