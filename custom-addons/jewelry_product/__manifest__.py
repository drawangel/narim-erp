{
    'name': 'Jewelry: Products',
    'version': '18.0.1.0.0',
    'category': 'Jewelry',
    'summary': 'Product extensions for jewelry business (weight, quality, origin)',
    'description': """
        Product extensions for jewelry, pawn shop and gold purchasing operations.

        Features:
        - Material quality definitions (24k, 18k, silver, etc.)
        - Product origin traceability
        - Weight tracking in grams
    """,
    'author': 'NarimERP',
    'license': 'LGPL-3',
    'depends': ['product', 'stock', 'jewelry_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/material_quality_data.xml',
        'views/material_quality_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}
