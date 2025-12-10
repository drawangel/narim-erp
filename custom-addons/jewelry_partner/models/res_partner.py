from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Override company_type to default to 'person' and rename label
    company_type = fields.Selection(
        selection=[('person', 'Particular'), ('company', 'Compañía')],
        default='person',
    )

    id_document_front = fields.Image(
        string='ID Document (Front)',
        help='Photo of the front side of the client ID document (DNI, passport, etc.)',
        max_width=1920,
        max_height=1920,
    )
    id_document_back = fields.Image(
        string='ID Document (Back)',
        help='Photo of the back side of the client ID document',
        max_width=1920,
        max_height=1920,
    )
