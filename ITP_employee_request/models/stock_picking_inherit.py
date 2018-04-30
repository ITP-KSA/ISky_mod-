# -*- coding: utf-8 -*-

from odoo import models,fields,api

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    emp_request_id = fields.Many2one('employee.request', 'Employee Request')
    partner_id = fields.Many2one('res.partner')
    type = fields.Selection([
        ('m', 'Publications'),
        ('fm', 'foodstuffs'),
        ('s', 'Watering'),
        ('a', 'Origins'),
        ('other', 'Other')
    ])

    @api.multi
    def write(self, vals):
        return_id = super(StockPickingInherit, self).write(vals)
        total_transfer = 0
        for rec in self:
            if len(rec.emp_request_id) > 0:
                employee_request = self.env['employee.request'].browse(rec.emp_request_id.id)
                for transfer in employee_request.transfer_ids:
                    if transfer.state == 'done':
                        total_transfer += 1
                if total_transfer == len(employee_request.transfer_ids):
                    employee_request.write({'state': 'final_done'})

            return return_id

class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    partner_id = fields.Many2one('res.partner')
