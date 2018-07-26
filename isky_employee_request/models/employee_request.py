# -*- coding: utf-8 -*-

from odoo import models,fields,api,_
from odoo.exceptions import ValidationError
from datetime import date

class EmployeeRequest(models.Model):
    _name='employee.request'
    _inherit = ['mail.thread']
    _rec_name='name'

    # get default user
    def get_user_id(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
        return employee_id

    # get company of login user
    def get_company_id(self):
        user_obj= self.env['res.users'].browse([(self.env.user.id)])
        return user_obj.company_id


    name = fields.Char(string='Sequence')
    employee_id = fields.Many2one('hr.employee',string='Responsible',default=get_user_id,required=True)
    company_id = fields.Many2one('res.company',string='Company',default=get_company_id)
    ordering_date = fields.Date(string='Scheduled Ordering Date',required=True,default=date.today().strftime('%Y-%m-%d'))
    schedule_date = fields.Date(string='Scheduled Date',required=True,default=date.today().strftime('%Y-%m-%d'))
    line_ids = fields.One2many('purchase.requisition.line','purchase_emp_request_id',string='Lines')
    transfer_ids = fields.One2many('stock.picking','emp_request_id',string='Transfers',readonly=True)
    is_confirmed = fields.Boolean(string='is_confirmed',default=False)
    refuse_reason = fields.Text(string='Refuse Reason')
    direct_manager_id = fields.Many2one('res.users', string='Direct Manager')
    departmental_manager_id = fields.Many2one('res.users', string='Departmental Manager')
    competent_department_id = fields.Many2one('hr.department', string='Specialist Department')
    is_need_competent_approve = fields.Boolean(string='Competent Department Approve', default = True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('sm_approve', 'Direct/Department Approved'),
        ('gm_approve', 'Administrative Approved'),
        ('admin_approve', 'Administrative Approved'),
        ('done', 'Done'),
        ('final_done', 'Final Done'),
        ('refuse', 'Refuse'),

    ], string='Status', readonly=True, select=True, copy=False, default='draft', track_visibility='onchange')
    employee_request_type_id = fields.Many2one('employee.request.type', string='Type')
    request_type = fields.Selection([('sample', 'Sample'), ('others', 'Others')], default='sample',
                                    string='Request Type', required=True)



    @api.constrains('schedule_date')
    def _get_schedule_date(self):
        for rec in self:
            if rec.schedule_date:
                if rec.ordering_date > rec.schedule_date:
                    raise ValidationError(_('Scheduled Date must be greater than or equal ordering date'))

    # Convert request from draft to open and send notification to his direct manager and department managers
    @api.multi
    def action_submit(self):
        partner_ids = []
        for rec in self:
            if rec.employee_id and rec.employee_id.department_id:
                ref = self.env['ir.model.data'].get_object_reference('mail', 'mt_comment')
                department_of_employee = self.env['hr.department'].search([('id', '=', rec.employee_id.department_id.id)])
                if not rec.line_ids:
                    raise ValidationError(_('Please create some Product lines.'))
                rec.write({'state': "open"})
                if rec.employee_id.parent_id.user_id.partner_id.id:
                    partner_ids.append((4, rec.employee_id.parent_id.user_id.partner_id.id))
                if department_of_employee.manager_id.user_id.partner_id.id:
                    partner_ids.append((4, department_of_employee.manager_id.user_id.partner_id.id))
                if len(partner_ids):
                    message_data = {
                                'type': 'notification',
                                'subject': _('Employee Request'),
                                'body': _('There is employee request that needs to approve'),
                                'partner_ids': partner_ids,
                                'subtype_id': ref[1],
                    }

                    self.env['mail.message'].create(message_data)



    # Convert request from open to direct/department approved, only direct/department manager can convert request from open to direct/department approve
    @api.multi
    def action_confirm_dm(self):
        ref = self.env['ir.model.data'].get_object_reference('mail', 'mt_comment')
        department_obj = self.env['hr.department']
        for rec in self:
            if rec.employee_id:
                if rec.employee_id.parent_id or rec.employee_id.department_id:
                    department_of_employee = department_obj.search([('id', '=', rec.employee_id.department_id.id)])
                    if self.env.uid != rec.employee_id.parent_id.user_id.id and self.env.uid != department_of_employee.manager_id.user_id.id:
                        raise ValidationError(_("Only Employee's Direct or Department Manager can approve!"))
                    else:
                        if self.env.uid == department_of_employee.manager_id.user_id.id:
                            rec.write({'state': "sm_approve"})
                        elif self.env.uid == rec.employee_id.parent_id.user_id.id:
                            rec.write({'state': 'sm_approve'})
                        else:
                            raise ValidationError(_("Only Employee's Direct or Department Manager can approve!"))
                else:
                    raise ValidationError(_("Only Employee's Direct or Department Manager can approve!"))
                if rec.employee_id.user_id:
                    message_data = {
                        'type': 'notification',
                        'subject': _('Employee Request'),
                        'body': _('Your request was approved by your manager'),
                        'partner_ids': [(4, [rec.employee_id.user_id.partner_id.id])],
                        'subtype_id': ref[1],
                    }
                    self.env['mail.message'].create(message_data)

    # Convert request from direct/deparment approval to administrative approval, only administrative manager can approve
    @api.multi
    def action_confirm_administrative(self):
        partner_ids = []
        ref = self.env['ir.model.data'].get_object_reference('mail', 'mt_comment')
        department_obj = self.env['hr.department']
        for rec in self:
            if rec.employee_id:
                administrative_department = department_obj.search([('administrative_dep', '=', True)])

                if administrative_department:
                    if self.env.uid != administrative_department.manager_id.user_id.id:
                        raise ValidationError(_("Only Administrative Manager can approve!"))
                    else:
                        if rec.is_need_competent_approve:
                            if rec.request_type == 'others':
                                rec.write({'state': 'admin_approve'})
                            else:
                                rec.write({'state': 'done'})
                        else:
                            self.write({'state': 'done'})
                        partner_ids.append(
                            (4, administrative_department.manager_id.user_id.partner_id.id))

                        message_data = {
                            'type': 'notification',
                            'subject': _('Employee Request'),
                            'body': _('There is employee request that needs to approve'),
                            'partner_ids': partner_ids,
                            'subtype_id': ref[1],
                        }

                        self.env['mail.message'].create(message_data)
                else:
                    raise ValidationError(_("System doesn't contain administrative department"))

    # Convert order lines to internal transfer
    def convert_order_line(self):
        ref = self.env['ir.model.data'].get_object_reference('mail', 'mt_comment')
        stock_move_obj = self.env['stock.move']
        stock_picking = self.env['stock.picking']
        administrative_dep = self.env['hr.department'].search([('administrative_dep', '=', True)])
        for rec in self:
            for line in rec.line_ids:
                line_picking = self.env['stock.picking.type'].search([('id', '=', line.stock_picking_type_id.id)])
                if administrative_dep and administrative_dep.location_id:
                    if rec.employee_id.department_id.location_id:
                        created_user = self.env['res.users'].browse(rec.employee_id.user_id.id)
                        stock_picking_obj = stock_picking.create({
                            'company_id': rec.company_id.id,
                            'location_dest_id': rec.employee_id.department_id.location_id.id,
                            'location_id': administrative_dep.location_id.id,
                            'move_type': 'direct',
                            'picking_type_id': line_picking.id,
                            'priority': '1',
                            'emp_request_id': rec.id,
                            'partner_id': created_user.partner_id.id

                        })

                        stock_move_obj.create({
                            'company_id': rec.company_id.id,
                            'location_dest_id': rec.employee_id.department_id.location_id.id,
                            'location_id': administrative_dep.location_id.id,
                            'date': date.today().strftime('%Y-%m-%d'),
                            'date_expected': date.today().strftime('%Y-%m-%d'),
                            'name': 'transfer',
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom_id.id,
                            'product_uom_qty': line.product_qty,
                            'procure_method': 'make_to_stock',
                            'picking_id': stock_picking_obj.id,
                            'partner_id': created_user.partner_id.id

                        })
                    else:
                        raise ValidationError(_('Department of Responsible has no location !!!'))
                else:
                    raise ValidationError(_('Administrative Department has no location!!'))
                    if rec.employee_id.user_id:
                        message_data = {
                            'type': 'notification',
                            'subject': _('Employee Request'),
                            'body': _('Your request was finally approved'),
                            'partner_ids': [(4, [rec.employee_id.user_id.partner_id.id])],
                            'subtype_id': ref[1],
                        }
                        self.env['mail.message'].create(message_data)

    @api.multi
    def action_confirm_done(self):
        partner_ids= []
        ref = self.env['ir.model.data'].get_object_reference('mail', 'mt_comment')
        administrative_affairs_department = self.env['hr.department'].search([('administrative_dep', '=', True)])
        for rec in self:
            if rec.employee_id:
                for line in rec.line_ids:
                    if not line.stock_picking_type_id:
                        raise ValidationError(_("Please enter stock picking type in lines"))
                if administrative_affairs_department:
                    if self.env.uid != administrative_affairs_department.manager_id.user_id.id:
                        raise ValidationError(_("Only Administrative Affairs manager can approve request"))
                    if rec.is_need_competent_approve:
                        for line in rec.line_ids:
                            if not line.product_id:
                                    raise ValidationError( _("Please enter product"))
                        if rec.request_type == 'others':
                            rec.write({'state': 'admin_approve'})
                        else:
                            rec.write({'state': 'done'})
                            rec.convert_order_line()
                            if rec.competent_department_id.manager_id and rec.competent_department_id.manager_id.user_id:
                                partner_ids.append((4, rec.competent_department_id.manager_id.user_id.partner_id.id))
                                message_data = {
                                    'type': 'notification',
                                    'subject': _('Employee Request'),
                                    'body': _('There is employee request that needs to approve'),
                                    'partner_ids': partner_ids,
                                    'subtype_id': ref[1],
                                }

                                self.env['mail.message'].create(message_data)
                        if rec.employee_id.user_id:
                            message_data = {
                                'type': 'notification',
                                'subject': _('Employee Request'),
                                'body': _('Your request was approved by administrative manager'),
                                'partner_ids': [(4, [rec.employee_id.user_id.partner_id.id])],
                                'subtype_id': ref[1],
                            }
                            self.env['mail.message'].create(message_data)
                    else:
                        for line in rec.line_ids:
                            if not line.product_id:
                                raise ValidationError(_("Please enter product"))
                        if rec.request_type == 'others':
                            rec.write({'state': 'done'})
                            rec.convert_order_line()

                else:
                    raise ValidationError(_("System doesn't contain Administrative Affairs to approve request"))

    # Competent Manager Approve

    @api.multi
    def action_confirm_competent(self):
        for rec in self:
            competent_dep_id = self.env['hr.department'].search([('id', '=', rec.competent_department_id.id)])
            if competent_dep_id.manager_id and self.env.uid == competent_dep_id.manager_id.user_id.id:
                rec.write({'state': 'done'})
                rec.convert_order_line()
            else:
                raise ValidationError(_("Only Competent department manager can approve the request"))

    @api.multi
    def action_confirm_gm(self):
        for rec in self:
            if rec.state == "sm_approve":
                rec.write({'state':'gm_approve'})


    # Refuse Employee Request
    @api.multi
    def action_refuse(self):
        for rec in self:
            if rec.employee_id and rec.employee_id.department_id:
                administrative_affairs_department = self.env['hr.department'].search([('administrative_dep', '=', True)])
                ref = self.env['ir.model.data'].get_object_reference('mail', 'mt_comment')
                department_of_employee = self.env['hr.department'].browse(rec.employee_id.department_id.id)
                if self.env.uid != rec.employee_id.parent_id.user_id.id and self.env.uid != department_of_employee.manager_id.user_id.id and self.env.uid != administrative_affairs_department.manager_id.user_id.id:
                        raise ValidationError(_("Only Employee's Direct or Department Manager can refuse request!"))
                else:
                    if not rec.refuse_reason:
                        raise ValidationError(_("You must enter the refuse reason"))
                    rec.write({'state': 'refuse'})
                    if rec.employee_id.user_id:
                        message_data = {
                                    'type': 'notification',
                                    'subject': _('Employee Request'),
                                    'body': _('Your request was refused'),
                                    'partner_ids': [(4, [rec.employee_id.user_id.partner_id.id])],
                                    'subtype_id': ref[1],
                        }
                        self.env['mail.message'].create(message_data)

    @api.multi
    def unlink(self):
        if any(rec.state not in ['draft'] for rec in self):
            raise ValidationError('You can only delete draft requests!')
        return super(EmployeeRequest, self).unlink()


    @api.model
    def create(self, vals):
        partner_ids = []
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.order.request')
        administrative_affairs_department = self.env['hr.department'].search([('administrative_dep', '=', True)])
        employee = self.env['hr.employee'].browse(vals['employee_id'])
        if administrative_affairs_department and administrative_affairs_department.manager_id and administrative_affairs_department.manager_id.user_id:
            partner_ids.append((4, administrative_affairs_department.manager_id.user_id.partner_id.id))
        elif employee and employee.parent_id and employee.parent_id.user_id:
            partner_ids.append((4, employee.parent_id.user_id.partner_id.id))
            vals['direct_manager_id'] = employee.parent_id.user_id.id
            if employee.department_id and employee.department_id.manager_id and employee.department_id.manager_id.user_id:
                partner_ids.append((4, employee.department_id.manager_id.user_id.partner_id.id))
                vals['departmental_manager_id'] = employee.department_id.manager_id.user_id.id
        if len(partner_ids):
            vals['message_follower_ids'] = partner_ids
        return super(EmployeeRequest, self).create(vals)


    @api.multi
    def write(self, vals):
        if 'is_need_competent_approve' in vals.keys():
            administrative_affairs_dep = self.env['hr.department'].search([('administrative_dep', '=', True)])
            if self.env.uid != administrative_affairs_dep.manager_id.user_id.id:
                raise ValidationError(_("Only Administrative Affairs manager can edit this field"))
        return super(EmployeeRequest, self).write(vals)
