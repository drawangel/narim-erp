{
    'name': 'Joyería: Informes Policiales',
    'version': '18.0.1.0.0',
    'category': 'Jewelry',
    'summary': 'Informes para Mossos d\'Esquadra (Excel/PDF)',
    'description': """
        Módulo de Informes Policiales para Joyerías

        Genera informes requeridos por los Mossos d'Esquadra para
        operaciones de compraventa de oro y empeños.

        Características:
        - Exportación a Excel con cabecera exacta requerida por la policía
        - Exportación a PDF con fotos de artículos y documentos de identidad
        - Filtros por fecha, estado, tienda y tipo de operación
        - Wizard intuitivo para generación de informes

        IMPORTANTE: La cabecera del Excel NO es editable. Se genera
        exactamente como requiere la policía para procesamiento automático.
    """,
    'author': 'NarimERP',
    'license': 'LGPL-3',
    'depends': [
        'jewelry_purchase_client',
        'jewelry_partner',
    ],
    'external_dependencies': {
        'python': ['xlsxwriter'],
    },
    'data': [
        'security/ir.model.access.csv',
        'wizard/police_report_wizard_views.xml',
        'report/police_report_pdf.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
}
