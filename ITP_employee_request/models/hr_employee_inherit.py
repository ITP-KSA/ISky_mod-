# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'


    @api.constrains('user_id')
    def _check_user_id(self):
        for rec in self:
            emp_objs = self.search([('user_id', '=', rec.user_id.id)])
            if len(emp_objs) > 1:
                raise ValidationError(_('There is another employee related to this user'))

