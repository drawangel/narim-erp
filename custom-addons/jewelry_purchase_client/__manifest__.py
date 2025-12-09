{
    'name': 'Jewelry: Client Purchases',
    'version': '18.0.2.4.0',
    'category': 'Jewelry',
    'summary': 'Gold and jewelry purchases from individuals with pawn support',
    'description': """
        Client Purchase Management for Jewelry Business

        This module handles purchases of gold and jewelry from individual clients
        (not suppliers). Key features:

        - Client purchase orders with detailed line items
        - Two operation types: Purchase (definitive) and Pawn (recoverable)
        - Legal blocking period before processing
        - Photo documentation per purchase line
        - Contract generation
        - State workflow:
          * Purchases: Draft -> Blocked -> Available -> Processed
          * Pawns: Draft -> Blocked -> Recoverable -> Available/Recovered
        - Pawn recovery with margin and daily surcharge calculation
        - Send items to inventory with optional repair tracking
        - Send items to smelting with individual tracking
        - Automatic state transitions via cron jobs
        - Automatic order completion when all lines are processed
    """,
    'author': 'NarimERP',
    'license': 'LGPL-3',
    'depends': ['mail', 'stock', 'sale_stock', 'point_of_sale', 'jewelry_base', 'jewelry_partner', 'jewelry_product'],
    'data': [
        'security/ir.model.access.csv',
        'security/client_purchase_security.xml',
        'data/sequence_data.xml',
        'data/cron_data.xml',
        'data/stock_location_data.xml',
        'data/smelting_sequence_data.xml',
        'wizard/force_unlock_wizard_views.xml',
        'wizard/send_to_inventory_wizard_views.xml',
        'wizard/smelt_all_wizard_views.xml',
        'wizard/receive_all_wizard_views.xml',
        'wizard/recovery_wizard_views.xml',
        'security/force_unlock_security.xml',
        'views/smelting_batch_views.xml',
        'views/client_purchase_views.xml',
        'views/product_views.xml',
        'views/pos_session_views.xml',
        'views/menu_views.xml',
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'jewelry_purchase_client/static/src/css/police_badge.css',
        ],
    },
    'installable': True,
    'application': False,
}
