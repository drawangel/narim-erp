{
    'name': 'Jewelry Partner',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Extends contacts with ID document photos',
    'description': """
        Extends res.partner with fields for storing ID document photos.

        Features:
        - ID document front photo
        - ID document back photo
        - Dedicated fields in contact form for easy access
    """,
    'author': 'NarimERP',
    'website': 'https://github.com/yourusername/NarimERP',
    'license': 'LGPL-3',
    'depends': ['jewelry_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
