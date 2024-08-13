from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pnt_redirect_url = fields.Char(string="Redirect URL", config_parameter='pnt.redirect.url')

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        redirect_url = self.env['ir.config_parameter'].sudo().get_param('pnt.redirect.url')
        redirect_app = self.env['pnt.redirect.app'].search([], limit=1)
        if not redirect_app:
            self.env['pnt.redirect.app'].create({'pnt_redirect_url': redirect_url})
        else:
            redirect_app.write({'pnt_redirect_url': redirect_url})
