# -*- coding: utf-8 -*-
from odoo import models,fields,api,_
from odoo.exceptions import ValidationError


class purchase_requisition_line(models.Model):
    _inherit ='purchase.requisition.line'

    purchase_emp_request_id = fields.Many2one('employee.request',string='Employee Request')
    product_id = fields.Many2one('product.product',string='Product',domain=[('type','!=','service'),('purchase_ok', '=', True)])
    department_id = fields.Many2one('hr.department', string='Department')
    justifications = fields.Text(string='Justifications')
    stock_picking_type_id = fields.Many2one('stock.picking.type', string='Stock Picking Type', domain="[('code','=','internal')]")
    description = fields.Text(string='Description',related='product_id.description_picking',store=True)
    specification = fields.Text(string='Specification')

    @api.onchange('product_id')
    def _get_uom_of_product(self):
        for rec in self:
            if rec.product_id:
                product_obj = self.env['product.product'].browse(rec.product_id.id)
                rec.product_uom_id = product_obj.uom_id.id
                rec.product_qty = 1.0


    # Prevent editting when request converts from draft
    @api.model
    def create(self, vals):
        if 'purchase_emp_request_id' in vals.keys() and vals['purchase_emp_request_id']:
            employee_request_obj = self.env['employee.request'].browse(vals['purchase_emp_request_id'])
            if employee_request_obj.state != 'draft':
                raise ValidationError(_('You can only add new item in draft state'))
        return super(purchase_requisition_line, self).create(vals)

    # Allow Competent manager to edit description in product lines
    @api.multi
    def write(self, vals):
        for rec in self:
            employee_request_obj = self.env['employee.request'].browse(rec.purchase_emp_request_id.id)
            if employee_request_obj.state == 'admin_approve':
                if rec.purchase_emp_request_id.competent_department_id.manager_id.user_id.id != self.env.uid:
                    raise ValidationError(_("Only Competent department manager can edit product line"))
            return super(purchase_requisition_line, self).write(vals)
