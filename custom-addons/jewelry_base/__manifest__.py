{
    'name': 'Jewelry Base',
    'version': '18.0.1.0.2',
    'category': 'Sales',
    'summary': 'Base module for jewelry business operations',
    'description': """
        Base module for jewelry, pawn shop and gold purchasing operations.

        Features:
        - Security groups (Operator / Manager)
        - Base configuration parameters
    """,
    'author': 'NarimERP',
    'website': 'https://github.com/yourusername/NarimERP',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'contacts', 'purchase'],
    'data': [
        'security/jewelry_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/purchase_menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
