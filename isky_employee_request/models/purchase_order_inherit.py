# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from operator import attrgetter

class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    refuse_case = fields.Text(string='Refuse Reason')

    @api.multi
    def button_cancel(self):
        for rec in self:
            if not rec.refuse_case:
                raise ValidationError(_("You must enter the refuse reason"))
            return super(PurchaseOrderInherit,self).button_cancel()

