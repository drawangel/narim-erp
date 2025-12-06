from odoo import fields, models


class MaterialQuality(models.Model):
    _name = 'jewelry.material.quality'
    _description = 'Material Quality'
    _order = 'sequence, name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Quality name (e.g., 24k, 18k, Sterling Silver)',
    )
    code = fields.Char(
        string='Code',
        help='Short code for quick reference',
    )
    material_type = fields.Selection(
        selection=[
            ('gold', 'Gold'),
            ('silver', 'Silver'),
            ('platinum', 'Platinum'),
            ('palladium', 'Palladium'),
            ('other', 'Other'),
        ],
        string='Material Type',
        required=True,
        default='gold',
    )
    purity_percent = fields.Float(
        string='Purity (%)',
        digits=(5, 2),
        help='Percentage of pure metal (e.g., 75.0 for 18k gold)',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order in selection lists',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Quality code must be unique!'),
        ('purity_range', 'CHECK(purity_percent >= 0 AND purity_percent <= 100)',
         'Purity must be between 0 and 100!'),
    ]
