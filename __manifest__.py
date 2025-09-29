# -*- coding: utf-8 -*-
{
    'name': "Sally's Flower Shop",
    'summary': "Manage a flower shop and track flower data",
    'description': "This module helps in managing a flower shop, from defining flower-specific attributes to tracking their lifecycle.",
    'author': "Your Name",
    'website': "https://www.yourwebsite.com",
    'category': 'Sales',
    'version': '1.0',
    'depends': ['base', 'sale', 'website_sale', 'stock'],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        
     
        'data/ir_config_parameter.xml',
        'data/actions.xml',
        
    
        'views/flower_views.xml',
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/product_website_template.xml',
        'views/warehouse_views.xml',
        
       
        'reports/paperformat.xml', 
        'reports/report_templates.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}