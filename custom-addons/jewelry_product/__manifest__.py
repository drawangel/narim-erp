{
    'name': 'Jewelry: Products',
    'version': '18.0.1.1.1',
    'category': 'Jewelry',
    'summary': 'Product extensions for jewelry business (weight, quality, origin)',
    'description': """
        Product extensions for jewelry, pawn shop and gold purchasing operations.

        Features:
        - Material quality definitions (24k, 18k, silver, etc.)
        - Product origin traceability
        - Weight tracking in grams
        - Repair tracking for items needing repair before sale
    """,
    'author': 'NarimERP',
    'license': 'LGPL-3',
    'depends': ['product', 'stock', 'point_of_sale', 'jewelry_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/material_quality_data.xml',
        'views/material_quality_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}
