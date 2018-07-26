# -*- coding: utf-8 -*-
{
    'name': "iSky Sale/Purchase Customizations",
    'version': '0.2',
    'author': "iSky Development",
    'summary': """Sale/Purchase Customizations""",
    'category': '',
    'description': """
iSky Sale/Purchase Customizations
====================================

Add customizations to Sale and Purchase cycles.
    """,
    'website': "http://www.iskydev.com",
    'depends': [
        'base',
        'account',
        'sale_management',
        'purchase',
        'stock',
        'project',
        'sale_timesheet',
    ],
    'data': [
        'views/isky_project_views.xml',
        'views/isky_product_views.xml',
        'views/isky_sale_order_line_tree.xml',
        'views/isky_account_invoice_lines_tree.xml',
        'views/isky_purchase_order_lines_tree.xml',
        'views/isky_stock_move_tree.xml',
        'views/isky_sale_order_view.xml',
        'views/isky_account_invoice_view.xml',
        'views/isky_stock_picking_view.xml',
        'reports/isky_report_stock_picking.xml',
        'reports/isky_sale_report_inherit.xml',
        'reports/isky_report_account_invoices.xml',
        # Menu Item
        'views/menuitems.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'auto_install': False,
}
