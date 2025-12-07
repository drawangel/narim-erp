from odoo import api, fields, models
from odoo.exceptions import UserError


class ReceiveAllWizard(models.TransientModel):
    _name = 'jewelry.receive.all.wizard'
    _description = 'Receive All Items Wizard'

    purchase_id = fields.Many2one(
        comodel_name='jewelry.client.purchase',
        string='Purchase Order',
        required=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        related='purchase_id.currency_id',
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        default=lambda self: self._default_warehouse_id(),
    )

    # Price calculation options
    price_mode = fields.Selection([
        ('same', 'Same as purchase price'),
        ('multiplier', 'Multiply purchase price'),
    ], string='Sale Price Mode', default='multiplier', required=True)
    price_multiplier = fields.Float(
        string='Price Multiplier',
        default=1.5,
        digits=(4, 2),
    )

    # Summary fields (computed)
    pending_count = fields.Integer(
        string='Items to Receive',
        compute='_compute_summary',
    )
    total_value = fields.Monetary(
        string='Total Purchase Value',
        compute='_compute_summary',
        currency_field='currency_id',
    )
    line_ids = fields.Many2many(
        comodel_name='jewelry.client.purchase.line',
        string='Items',
        compute='_compute_summary',
    )

    @api.model
    def _default_warehouse_id(self):
        return self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )

    @api.depends('purchase_id')
    def _compute_summary(self):
        for wizard in self:
            pending_lines = wizard.purchase_id.line_ids.filtered(
                lambda l: l.line_state == 'pending'
            )
            wizard.pending_count = len(pending_lines)
            wizard.total_value = sum(pending_lines.mapped('price'))
            wizard.line_ids = pending_lines

    def action_confirm_receive(self):
        """Create products for all pending items and add to inventory."""
        self.ensure_one()

        pending_lines = self.purchase_id.line_ids.filtered(
            lambda l: l.line_state == 'pending'
        )

        if not pending_lines:
            raise UserError('No pending items to receive.')

        if self.purchase_id.state != 'available':
            raise UserError('Order must be in Available state.')

        # Get destination location
        location_dest = self.warehouse_id.lot_stock_id

        # Get inventory location for stock moves
        location_src = self.env['stock.location'].search(
            [('usage', '=', 'inventory'), ('company_id', 'in', [self.env.company.id, False])],
            limit=1
        )

        # Create products one by one to avoid batch creation issues
        created_products = []
        for line in pending_lines:
            sale_price = line.price
            if self.price_mode == 'multiplier':
                sale_price = line.price * self.price_multiplier

            # Generate SKU from purchase reference
            sku = line._generate_sku()

            # Create product template (type='consu' + is_storable=True for inventory tracking in Odoo 18)
            template = self.env['product.template'].create({
                'name': line.description,
                'default_code': sku,
                'type': 'consu',
                'is_storable': True,
                'standard_price': line.price,
                'list_price': sale_price,
                'origin_type': 'client',
                'jewelry_quality_id': line.quality_id.id if line.quality_id else False,
                'jewelry_weight': line.weight,
                'client_purchase_line_id': line.id,
                'needs_repair': False,
                'ready_for_sale': True,
            })
            product = template.product_variant_id
            created_products.append(product)

            # Create stock move
            move = self.env['stock.move'].create({
                'name': f'Client purchase entry: {product.name}',
                'product_id': product.id,
                'product_uom_qty': 1.0,
                'product_uom': product.uom_id.id,
                'location_id': location_src.id,
                'location_dest_id': location_dest.id,
                'price_unit': line.price,
            })
            move._action_confirm()
            move._action_assign()
            # In Odoo 18, set quantity (done qty) before completing
            move.quantity = 1.0
            move._action_done()

            # Update line
            line.write({
                'product_id': product.id,
                'line_state': 'in_inventory',
            })

        # Log to chatter
        items_summary = '<br/>'.join([
            f"- <a href='/web#id={p.id}&model=product.product'>{p.name}</a>"
            for p in created_products
        ])

        self.purchase_id.message_post(
            body=f"<b>{len(created_products)}</b> items received into inventory:<br/>"
                 f"{items_summary}<br/><br/>"
                 f"<b>Warehouse:</b> {self.warehouse_id.name}<br/>"
                 f"<b>Price mode:</b> {'Same as purchase' if self.price_mode == 'same' else f'x{self.price_multiplier}'}",
            subject='Items received into inventory',
            message_type='notification',
        )

        # Check if order should transition to processed
        pending_lines[0]._check_order_completion()

        # Return notification and close
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'{len(created_products)} products created and added to inventory',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
