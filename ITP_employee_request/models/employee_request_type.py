# -*- coding: utf-8 -*-

from odoo import models,fields,api,_

class EmployeeRequestType(models.Model):
    _name = 'employee.request.type'

    name = fields.Char(string='Name')