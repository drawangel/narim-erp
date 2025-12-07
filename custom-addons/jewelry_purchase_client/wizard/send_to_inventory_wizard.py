from odoo import api, fields, models
from odoo.exceptions import UserError


class SendToInventoryWizard(models.TransientModel):
    _name = 'jewelry.send.to.inventory.wizard'
    _description = 'Send to Inventory Wizard'

    line_id = fields.Many2one(
        comodel_name='jewelry.client.purchase.line',
        string='Purchase Line',
        required=True,
        readonly=True,
    )
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True,
        default=lambda self: self._default_warehouse_id(),
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='line_id.currency_id',
        readonly=True,
    )

    # Display fields from line
    line_description = fields.Text(
        related='line_id.description',
        string='Item Description',
        readonly=True,
    )
    line_price = fields.Monetary(
        related='line_id.price',
        string='Purchase Price',
        currency_field='currency_id',
        readonly=True,
    )
    line_quality_id = fields.Many2one(
        related='line_id.quality_id',
        string='Quality',
        readonly=True,
    )
    line_weight = fields.Float(
        related='line_id.weight',
        string='Weight (g)',
        readonly=True,
    )

    # Product data
    product_name = fields.Char(
        string='Product Name',
        required=True,
    )
    sale_price = fields.Monetary(
        string='Sale Price',
        currency_field='currency_id',
    )

    # Repair options
    needs_repair = fields.Boolean(
        string='Needs Repair',
        default=False,
    )
    repair_notes = fields.Text(
        string='Repair Notes',
        help='Describe repairs needed (polishing, soldering, setting adjustment, etc.)',
    )
    repair_cost = fields.Monetary(
        string='Estimated Repair Cost',
        currency_field='currency_id',
    )

    # Computed summary
    total_cost = fields.Monetary(
        string='Total Cost',
        compute='_compute_total_cost',
        currency_field='currency_id',
    )
    destination_location = fields.Char(
        string='Destination',
        compute='_compute_destination_location',
    )

    @api.model
    def _default_warehouse_id(self):
        return self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)], limit=1
        )

    @api.depends('line_id.price', 'repair_cost')
    def _compute_total_cost(self):
        for wizard in self:
            wizard.total_cost = (wizard.line_id.price or 0.0) + (wizard.repair_cost or 0.0)

    @api.depends('needs_repair', 'warehouse_id')
    def _compute_destination_location(self):
        for wizard in self:
            if wizard.needs_repair:
                wizard.destination_location = 'Pending Repair'
            elif wizard.warehouse_id:
                wizard.destination_location = wizard.warehouse_id.lot_stock_id.display_name
            else:
                wizard.destination_location = ''

    @api.onchange('needs_repair')
    def _onchange_needs_repair(self):
        if not self.needs_repair:
            self.repair_notes = False
            self.repair_cost = 0.0

    def action_create_product(self):
        """Create product from purchase line and add to inventory."""
        self.ensure_one()

        if self.line_id.line_state == 'in_inventory':
            raise UserError('This item has already been sent to inventory.')

        # 1. Generate SKU from purchase reference
        sku = self.line_id._generate_sku()

        # 2. Create product template (type='consu' + is_storable=True for inventory tracking in Odoo 18)
        template_vals = {
            'name': self.product_name,
            'default_code': sku,
            'type': 'consu',
            'is_storable': True,
            'standard_price': self.line_id.price,
            'list_price': self.sale_price or 0.0,
            'origin_type': 'client',
            'jewelry_quality_id': self.line_id.quality_id.id if self.line_id.quality_id else False,
            'jewelry_weight': self.line_id.weight,
            'client_purchase_line_id': self.line_id.id,
            'needs_repair': self.needs_repair,
            'repair_notes': self.repair_notes,
            'repair_cost': self.repair_cost,
            'ready_for_sale': not self.needs_repair,
            'available_in_pos': not self.needs_repair,
        }
        template = self.env['product.template'].create(template_vals)
        product = template.product_variant_id

        # 3. Determine destination location
        if self.needs_repair:
            location_dest = self.env.ref(
                'jewelry_purchase_client.stock_location_pending_repair'
            )
        else:
            location_dest = self.warehouse_id.lot_stock_id

        # 3. Create stock move (inventory adjustment entry)
        # In Odoo 18, inventory location is company-dependent via property_stock_inventory
        location_src = product.property_stock_inventory or self.env['stock.location'].search(
            [('usage', '=', 'inventory'), ('company_id', 'in', [self.env.company.id, False])],
            limit=1
        )

        move = self.env['stock.move'].create({
            'name': f'Client purchase entry: {product.name}',
            'product_id': product.id,
            'product_uom_qty': 1.0,
            'product_uom': product.uom_id.id,
            'location_id': location_src.id,
            'location_dest_id': location_dest.id,
            'price_unit': self.line_id.price,
        })
        move._action_confirm()
        move._action_assign()
        # In Odoo 18, set quantity (done qty) before completing
        move.quantity = 1.0
        move._action_done()

        # 4. Link product to line and update state
        self.line_id.write({
            'product_id': product.id,
            'line_state': 'in_inventory',
        })

        # 5. Log to chatter
        repair_msg = ' (pending repair)' if self.needs_repair else ''
        self.line_id.order_id.message_post(
            body=f"Item '<b>{self.line_id.description}</b>' sent to inventory as "
                 f"product <a href='/web#id={product.id}&model=product.product'>"
                 f"{product.name}</a>{repair_msg}.",
            subject='Item sent to inventory',
            message_type='notification',
        )

        # 6. Check if all lines are processed (triggers auto-transition to 'processed')
        self.line_id._check_order_completion()

        # 7. Return action to view the created product
        return {
            'type': 'ir.actions.act_window',
            'name': 'Created Product',
            'res_model': 'product.product',
            'res_id': product.id,
            'view_mode': 'form',
            'target': 'current',
        }
