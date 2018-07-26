from odoo import api, fields, models


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    purchase_limit_budget = fields.Float(string='Purchase Limit Budget')

    def set_values(self):
        set_param = self.env['ir.config_parameter'].set_param
        set_param('purchase_limit_budget', (self.purchase_limit_budget))
        super(ResConfigSettingsInherit, self).set_values()

    @api.multi
    def get_values(self):
        res = super(ResConfigSettingsInherit, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res.update(
            purchase_limit_budget = float(get_param('purchase_limit_budget'))
        )
        return res
