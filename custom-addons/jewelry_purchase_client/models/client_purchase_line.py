from odoo import api, fields, models


class ClientPurchaseOrderLine(models.Model):
    _name = 'jewelry.client.purchase.line'
    _description = 'Client Purchase Order Line'
    _order = 'order_id, sequence, id'

    order_id = fields.Many2one(
        comodel_name='jewelry.client.purchase',
        string='Order',
        required=True,
        ondelete='cascade',
        index=True,
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    description = fields.Text(
        string='Description',
        required=True,
        help='Detailed description of the item',
    )
    quality_id = fields.Many2one(
        comodel_name='jewelry.material.quality',
        string='Quality',
        help='Material quality (e.g., 18k gold, sterling silver)',
    )
    weight = fields.Float(
        string='Weight (g)',
        digits=(10, 3),
        help='Weight in grams',
    )
    price = fields.Monetary(
        string='Amount',
        required=True,
        help='Amount paid to client for this item',
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id',
        store=True,
    )
    company_id = fields.Many2one(
        related='order_id.company_id',
        store=True,
    )
    state = fields.Selection(
        related='order_id.state',
        store=True,
    )

    # Image attachments
    image_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='client_purchase_line_image_rel',
        column1='line_id',
        column2='attachment_id',
        string='Photos',
        help='Photos of the item for documentation',
    )
    image_count = fields.Integer(
        string='Photo Count',
        compute='_compute_image_count',
    )

    # Optional product link (for items that become inventory)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Created Product',
        readonly=True,
        help='Product created from this line when processed',
    )

    @api.depends('image_ids')
    def _compute_image_count(self):
        for line in self:
            line.image_count = len(line.image_ids)

    @api.onchange('quality_id')
    def _onchange_quality_id(self):
        """Auto-fill description with quality name if empty."""
        if self.quality_id and not self.description:
            self.description = self.quality_id.name

    def action_view_images(self):
        """Open images in a gallery view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Photos - {self.description or "Item"}',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,form',
            'domain': [('id', 'in', self.image_ids.ids)],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }
