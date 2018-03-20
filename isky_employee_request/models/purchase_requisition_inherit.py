# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseRequisitionInherit(models.Model):
    _inherit = 'purchase.requisition'

    department_id = fields.Many2one('hr.department',string='Department Requested')
    employee_request_id = fields.Many2one('employee.request', string='Employee Request', domain="[('state','=','done')]")
    estimated_budget = fields.Float(string='Estimated budget')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('submit', _('Submitted')),
         ('in_progress', 'Confirmed'),
         ('open', 'Bid Selection'),
         ('done', 'PO Created'),
         ('cancel', 'Cancelled')], string='Status', track_visibility='onchange', required=True)
    is_employee_required = fields.Boolean(string='Contain Request', default=False)

    @api.multi
    def submitted_call(self):
        for rec in self:
            rec.write({'state': 'submit'})

    @api.multi
    def show_confirm(self):
        for rec in self:
            rec.write({'state':'in_progress'})


    @api.onchange('employee_request_id')
    def _get_line_ids(self):
        for rec in self:
            if rec.employee_request_id:
                emp_req_obj = self.env['employee.request'].browse((self.employee_request_id.id))
                if emp_req_obj:
                    rec.line_ids = [(0, 0, {'product_id': line.product_id.id,
                                            'product_qty': line.product_qty,
                                            'justifications':line.justifications,
                                            'schedule_date':line.purchase_emp_request_id.schedule_date}) for line in emp_req_obj.line_ids]



    # Check estimated budget and number of request of quotation
    @api.multi
    def write(self, vals):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        purchase_limit_budget = float(get_param('purchase_limit_budget'))
        if 'state' in vals.keys() and vals['state'] == "in_progress":
            if 'estimated_budget' in vals.keys() and vals['estimated_budget'] >= purchase_limit_budget:
                if 'purchase_ids' in vals.keys() and len(vals['purchase_ids']) < 3:
                    raise ValidationError(_('Request of Quotation must be more than 3'))
                elif len(self.purchase_ids) < 3:
                    raise ValidationError(_('Request of Quotation must be more than 3'))
            if self.estimated_budget >= purchase_limit_budget:
                if 'purchase_ids' in vals.keys() and len(vals['purchase_ids']) < 3:
                    raise ValidationError(_('Request of Quotation must be more than 3'))
                elif len(self.purchase_ids) < 3:
                    raise ValidationError(_('Request of Quotation must be more than 3'))
            if 'estimated_budget' not in vals.keys():
                if self.estimated_budget == 0.0:
                    raise ValidationError(_('You must enter estimated budget'))
        return super(PurchaseRequisitionInherit, self).write(vals)


class ProductUomInherit(models.Model):
    _inherit = 'product.uom'

    @api.multi
    def _compute_price(self, price, to_unit):
        if not self or not price or not to_unit or self == to_unit:
            return price
        if self.category_id.id != to_unit.category_id.id:
            return price
        amount = price * self.factor
        if to_unit:
            amount = amount / to_unit.factor
        return amount



