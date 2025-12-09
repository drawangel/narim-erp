{
    'name': 'Jewelry: Products',
    'version': '18.0.1.2.0',
    'category': 'Jewelry',
    'summary': 'Product extensions for jewelry business (type, weight, quality, origin)',
    'description': """
        Product extensions for jewelry, pawn shop and gold purchasing operations.

        Features:
        - Jewelry type definitions (Ring, Necklace, Earrings, etc.) with keyword inference
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
        'data/jewelry_type_data.xml',
        'data/material_quality_data.xml',
        'views/jewelry_type_views.xml',
        'views/material_quality_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}
