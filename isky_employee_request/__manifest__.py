# -*- coding: utf-8 -*-

{
    'name': "Employee Request",
    'version': '0.2',

    'summary': """ Employee Request """,

    'description': """
            In this module add employee request menu .
            employee can make request for products and direct manager for this employee approve and create purchase requisition and sector manager approve also .
            finally when general manager approve this request, it create internal transfer for all requested products to location of management department.""",

    'author': "Isky Development Team",

    'website': "http://iskydev.com/",

    'depends': ['base','hr','purchase','purchase_requisition'],

    'data': [
        'security/isky_employee_request_security.xml',
        'security/ir.model.access.csv',
        'views/employee_request_sequence.xml',
        'views/employee_request.xml',
        'views/hr_department_inherit.xml',
        'views/purchase_requisition_inherit.xml',
        'views/purchase_order_inherit.xml',
        'views/stock_picking_inherit.xml',
        'views/purchase_config_settings_inherit.xml',
        'views/isky_employee_request_type.xml',
        'reports/report_stock_picking_inherit.xml',
        'reports/report_purchase_requisition.xml',
        'views/menuitems.xml',



    ],
}
