from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Traceability to client purchase - defined here because the referenced model
    # (jewelry.client.purchase.line) is in this module
    client_purchase_line_id = fields.Many2one(
        comodel_name='jewelry.client.purchase.line',
        string='Purchase Origin',
        readonly=True,
        help='The client purchase line that originated this product',
    )
