{
    'name': 'Jewelry: Client Purchases',
    'version': '18.0.1.0.0',
    'category': 'Jewelry',
    'summary': 'Gold and jewelry purchases from individuals',
    'description': """
        Client Purchase Management for Jewelry Business

        This module handles purchases of gold and jewelry from individual clients
        (not suppliers). Key features:

        - Client purchase orders with detailed line items
        - Legal blocking period before smelting
        - Photo documentation per purchase line
        - Contract generation
        - State workflow: Draft → Confirmed → Blocked → Available → Processed
    """,
    'author': 'NarimERP',
    'license': 'LGPL-3',
    'depends': ['mail', 'jewelry_base', 'jewelry_partner', 'jewelry_product'],
    'data': [
        'security/ir.model.access.csv',
        'security/client_purchase_security.xml',
        'data/sequence_data.xml',
        'data/cron_data.xml',
        'views/client_purchase_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
}
