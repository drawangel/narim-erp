from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _description = 'Product Template'

    origin_type = fields.Selection(
        selection=[
            ('supplier', 'Supplier Purchase'),
            ('client', 'Client Purchase'),
            ('pawn', 'Forfeited Pawn'),
        ],
        string='Origin Type',
        help='How this product entered the inventory',
    )
    jewelry_quality_id = fields.Many2one(
        comodel_name='jewelry.material.quality',
        string='Material Quality',
        help='Quality/purity of the material',
    )
    jewelry_weight = fields.Float(
        string='Jewelry Weight (g)',
        digits=(10, 3),
        help='Weight in grams for precious metals',
    )
