from odoo import api, fields, models
from odoo.exceptions import UserError


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
    jewelry_type_id = fields.Many2one(
        comodel_name='jewelry.type',
        string='Tipo de Joya',
        help='Tipo de artículo (Anillo, Collar, Pendientes, etc.)',
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

    # Repair-related fields
    needs_repair = fields.Boolean(
        string='Needs Repair',
        default=False,
        help='Indicates if the product needs repair before sale',
    )
    repair_notes = fields.Text(
        string='Repair Notes',
        help='Description of repairs needed (polishing, soldering, setting, etc.)',
    )
    repair_cost = fields.Monetary(
        string='Repair Cost',
        currency_field='currency_id',
        help='Estimated or actual cost of repair',
    )
    ready_for_sale = fields.Boolean(
        string='Ready for Sale',
        default=True,
        help='Determines if the product can be sold',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.onchange('needs_repair')
    def _onchange_needs_repair(self):
        """Update ready_for_sale when needs_repair changes."""
        if self.needs_repair:
            self.ready_for_sale = False

    def action_complete_repair(self):
        """Mark repair as completed and move to sellable stock."""
        self.ensure_one()

        if not self.needs_repair:
            raise UserError('This product is not marked as needing repair.')

        # Update cost with repair cost
        if self.repair_cost:
            self.standard_price += self.repair_cost

        # Get repair location
        location_repair = self.env.ref(
            'jewelry_purchase_client.stock_location_pending_repair',
            raise_if_not_found=False,
        )

        if location_repair:
            # Find quant in repair location
            quant = self.env['stock.quant'].search([
                ('product_id', 'in', self.product_variant_ids.ids),
                ('location_id', '=', location_repair.id),
                ('quantity', '>', 0),
            ], limit=1)

            if quant:
                # Get destination warehouse stock location
                warehouse = location_repair.warehouse_id or self.env['stock.warehouse'].search(
                    [('company_id', '=', self.env.company.id)], limit=1
                )
                location_dest = warehouse.lot_stock_id if warehouse else False

                if location_dest:
                    # Create move from repair location to stock
                    move = self.env['stock.move'].create({
                        'name': f'Repair completed: {self.name}',
                        'product_id': quant.product_id.id,
                        'product_uom_qty': quant.quantity,
                        'product_uom': self.uom_id.id,
                        'location_id': location_repair.id,
                        'location_dest_id': location_dest.id,
                    })
                    move._action_confirm()
                    move._action_assign()
                    move._action_done()

        # Update flags
        self.write({
            'needs_repair': False,
            'ready_for_sale': True,
            'available_in_pos': True,
        })
