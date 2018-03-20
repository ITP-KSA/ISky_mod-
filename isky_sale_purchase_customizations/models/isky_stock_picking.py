# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class Picking(models.Model):
    _inherit = "stock.picking"

    client_po = fields.Char(string="Client's P.O")

    @api.multi
    def button_validate(self):
        for move in self.move_lines:
            available_quantity = self.env['stock.quant']._get_available_quantity(move.product_id, move.location_id)
            if  move.quantity_done < 1:
                raise ValidationError("Done cant be zero")
            if available_quantity < move.quantity_done:
                raise ValidationError("Please check the quantity available for this product")
        return super(Picking,self).button_validate()