{
    'name': 'NarimERP Installer',
    'version': '1.0.3',
    'category': 'Hidden',
    'summary': 'Módulo maestro para instalar NarimERP',
    'description': """
        Este módulo instala automáticamente todos los componentes de NarimERP.
        Solo necesitas instalar este módulo y él se encargará de las dependencias.
    """,
    'author': 'NarimERP',
    'depends': [
        # Módulos Base Odoo (OOTB)
        'base',
        'contacts',
        'sale_management',
        'purchase',
        'stock',
        'account',
        'repair',
        'point_of_sale',
        'mail',
        'utm',  # Required for link_tracker menu
        'link_tracker',
        'spreadsheet_dashboard',

        # Módulos Custom NarimERP
        'jewelry_base',
        'jewelry_partner',
        'jewelry_product',
        'jewelry_purchase_client',
        'jewelry_pawn',
        'jewelry_report',
    ],
    'post_init_hook': 'post_init_hook',
    'data': [
        'data/menu_sequence_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}

