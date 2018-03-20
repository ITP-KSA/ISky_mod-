from odoo import models, fields, api


class iSkyprojectTaskInh(models.Model):
    _inherit = 'project.task'

    badge_number = fields.Text(string="Badge Number")
    contact_info = fields.Text(string="Contact Info")
    special_sale = fields.Boolean(string="Special Sale")
