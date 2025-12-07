from odoo import api, fields, models
from odoo.exceptions import UserError


class SmeltAllWizard(models.TransientModel):
    _name = 'jewelry.smelt.all.wizard'
    _description = 'Smelt All Items Wizard'

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

    # Summary fields (computed)
    pending_count = fields.Integer(
        string='Items to Smelt',
        compute='_compute_summary',
    )
    total_weight = fields.Float(
        string='Total Weight (g)',
        compute='_compute_summary',
        digits=(10, 3),
    )
    total_value = fields.Monetary(
        string='Total Value',
        compute='_compute_summary',
        currency_field='currency_id',
    )
    line_ids = fields.Many2many(
        comodel_name='jewelry.client.purchase.line',
        string='Items',
        compute='_compute_summary',
    )

    @api.depends('purchase_id')
    def _compute_summary(self):
        for wizard in self:
            pending_lines = wizard.purchase_id.line_ids.filtered(
                lambda l: l.line_state == 'pending'
            )
            wizard.pending_count = len(pending_lines)
            wizard.total_weight = sum(pending_lines.mapped('weight'))
            wizard.total_value = sum(pending_lines.mapped('price'))
            wizard.line_ids = pending_lines

    def action_confirm_smelt(self):
        """Send all pending items to smelting."""
        self.ensure_one()

        pending_lines = self.purchase_id.line_ids.filtered(
            lambda l: l.line_state == 'pending'
        )

        if not pending_lines:
            raise UserError('No pending items to send to smelting.')

        if self.purchase_id.state != 'available':
            raise UserError('Order must be in Available state.')

        # Create smelting batch for traceability
        batch = self.env['jewelry.smelting.batch'].create({
            'date': fields.Date.today(),
        })

        # Update all lines to smelting state with batch reference
        pending_lines.write({
            'line_state': 'to_smelting',
            'smelting_batch_id': batch.id,
        })

        # Log to chatter with batch reference
        self.purchase_id.message_post(
            body=f"<b>{len(pending_lines)}</b> items sent to smelting<br/>"
                 f"<ul>"
                 f"<li>Batch: <a href='/web#id={batch.id}&model=jewelry.smelting.batch'>{batch.name}</a></li>"
                 f"<li>Total weight: {self.total_weight:.3f} g</li>"
                 f"<li>Total value: {self.total_value:.2f} {self.currency_id.symbol}</li>"
                 f"</ul>",
            subject='Items sent to smelting',
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
                'message': f'{len(pending_lines)} items sent to smelting',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }
