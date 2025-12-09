from odoo import api, fields, models


class JewelryType(models.Model):
    """Configurable jewelry types with keyword-based inference."""

    _name = 'jewelry.type'
    _description = 'Tipo de Joya'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nombre',
        required=True,
        translate=True,
        help='Nombre del tipo de joya (ej: Anillo, Collar)',
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=10,
        help='Orden en las listas desplegables',
    )
    keywords = fields.Text(
        string='Palabras Clave',
        help='Palabras separadas por comas para auto-detección (ej: "anillo, alianza, sortija")',
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        help='Dejar vacío para compartir entre todas las compañías',
    )

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         'Jewelry type name must be unique per company!'),
    ]

    def _get_keyword_list(self):
        """Return list of lowercase keywords for this type."""
        self.ensure_one()
        if not self.keywords:
            return []
        return [kw.strip().lower() for kw in self.keywords.split(',') if kw.strip()]

    @api.model
    def infer_from_description(self, description):
        """
        Infer jewelry type from description using keyword matching.

        Args:
            description: Text description to analyze

        Returns:
            jewelry.type record or empty recordset if no match
        """
        if not description:
            return self.browse()

        description_lower = description.lower()

        # Search all active types with keywords
        types = self.search([
            ('keywords', '!=', False),
            ('active', '=', True),
            '|',
            ('company_id', '=', False),
            ('company_id', '=', self.env.company.id),
        ])

        best_match = self.browse()
        best_score = 0

        for jewelry_type in types:
            keywords = jewelry_type._get_keyword_list()
            if not keywords:
                continue

            # Count matching keywords (simple scoring)
            score = sum(1 for kw in keywords if kw in description_lower)

            if score > best_score:
                best_score = score
                best_match = jewelry_type

        return best_match
