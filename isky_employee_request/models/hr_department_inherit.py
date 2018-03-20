# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    location_id = fields.Many2one('stock.location',string='Location')
    administrative_dep = fields.Boolean(string='Administrative Affairs Department')

    @api.constrains('administrative_dep')
    def _check_only_one_administrative_dep(self):
        for rec in self:
            administrative_dep_objs = self.env['hr.department'].search([('administrative_dep', '=', True)])
            if len(administrative_dep_objs) > 1:
                raise ValidationError(_('The system contains only one administrative Affairs.'))

