from odoo import models, fields, api


class PntRedirectApp(models.Model):
    _name = "pnt.redirect.app"
    _description = "App module that redirects to a custom link."
    _rec_name = "pnt_redirect_url"

    pnt_redirect_url = fields.Char(string="URL")

    @api.model
    def get_redirect_action(self):
        redirect_url = self.search([], limit=1).pnt_redirect_url
        if not redirect_url:
            redirect_url = 'https://vda10-2020.sek.net/erpsek-master/'
        action = {
            'type': 'ir.actions.act_url',
            'url': redirect_url,
            'target': 'new',
        }
        return action
