from odoo import api, fields, models


class SmeltingBatch(models.Model):
    _name = 'jewelry.smelting.batch'
    _description = 'Smelting Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'name'

    name = fields.Char(
        string='Reference',
        required=True,
        readonly=True,
        default='New',
        copy=False,
        tracking=True,
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    line_ids = fields.One2many(
        comodel_name='jewelry.client.purchase.line',
        inverse_name='smelting_batch_id',
        string='Items',
    )
    line_count = fields.Integer(
        string='Item Count',
        compute='_compute_totals',
        store=True,
    )
    total_weight = fields.Float(
        string='Total Weight (g)',
        compute='_compute_totals',
        store=True,
        digits=(10, 3),
    )
    total_value = fields.Monetary(
        string='Total Value',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Smelter'),
        ('received', 'Receipt Confirmed'),
    ], string='State', default='draft', required=True, tracking=True)

    smelter_id = fields.Many2one(
        comodel_name='res.partner',
        string='Smelter',
        domain="[('is_company', '=', True)]",
        tracking=True,
    )
    notes = fields.Text(string='Notes')

    # Receipt information
    receipt_date = fields.Date(string='Receipt Date')
    receipt_weight = fields.Float(
        string='Receipt Weight (g)',
        digits=(10, 3),
        help='Weight confirmed by smelter on receipt',
    )
    receipt_reference = fields.Char(
        string='Receipt Reference',
        help='Smelter receipt or invoice reference',
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name, company_id)',
         'Reference must be unique per company!'),
    ]

    @api.depends('line_ids', 'line_ids.weight', 'line_ids.price')
    def _compute_totals(self):
        for batch in self:
            batch.line_count = len(batch.line_ids)
            batch.total_weight = sum(batch.line_ids.mapped('weight'))
            batch.total_value = sum(batch.line_ids.mapped('price'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'jewelry.smelting.batch'
                ) or 'New'
        return super().create(vals_list)

    def action_send(self):
        """Mark batch as sent to smelter."""
        for batch in self:
            batch.write({'state': 'sent'})
            batch.message_post(
                body=f"Batch sent to smelter: {batch.smelter_id.name or 'Not specified'}",
                subject='Batch Sent',
                message_type='notification',
            )
        return True

    def action_confirm_receipt(self):
        """Mark batch as receipt confirmed."""
        for batch in self:
            batch.write({
                'state': 'received',
                'receipt_date': batch.receipt_date or fields.Date.today(),
            })
            batch.message_post(
                body=f"Receipt confirmed. Weight: {batch.receipt_weight:.3f}g, "
                     f"Reference: {batch.receipt_reference or 'N/A'}",
                subject='Receipt Confirmed',
                message_type='notification',
            )
        return True

    def action_reset_draft(self):
        """Reset batch to draft state."""
        for batch in self:
            batch.write({'state': 'draft'})
        return True
