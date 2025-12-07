from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError


class ClientPurchaseOrder(models.Model):
    _name = 'jewelry.client.purchase'
    _description = 'Client Purchase Order'
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
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client',
        required=True,
        tracking=True,
        domain="[('is_company', '=', False)]",
        help='Individual client selling gold/jewelry',
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
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        tracking=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    line_ids = fields.One2many(
        comodel_name='jewelry.client.purchase.line',
        inverse_name='order_id',
        string='Lines',
        copy=True,
    )
    amount_total = fields.Monetary(
        string='Total Amount',
        compute='_compute_amount_total',
        store=True,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('blocked', 'Blocking Period'),
            ('available', 'Available'),
            ('processed', 'Processed'),
            ('cancelled', 'Cancelled'),
        ],
        string='State',
        default='draft',
        required=True,
        tracking=True,
        index=True,
    )
    notes = fields.Text(
        string='Internal Notes',
    )
    total_image_count = fields.Integer(
        string='Total Photos',
        compute='_compute_total_image_count',
    )

    # Blocking period fields
    blocking_days = fields.Integer(
        string='Blocking Days',
        compute='_compute_blocking_days',
        help='Number of days items must be held (from configuration)',
    )
    blocking_end_date = fields.Date(
        string='Blocking End Date',
        compute='_compute_blocking_end_date',
        store=True,
        help='Date when items become available for processing',
    )
    days_remaining = fields.Integer(
        string='Days Remaining',
        compute='_compute_days_remaining',
        help='Days until blocking period ends',
    )
    can_process = fields.Boolean(
        string='Can Process',
        compute='_compute_can_process',
        help='Whether items can be sent to smelting',
    )
    all_lines_processed = fields.Boolean(
        string='All Lines Processed',
        compute='_compute_all_lines_processed',
        store=True,
        help='True when all lines have been sent to inventory or smelting',
    )

    # Force unlock audit fields
    force_unlocked = fields.Boolean(
        string='Force Unlocked',
        default=False,
        copy=False,
        help='Indicates if blocking period was manually skipped',
    )
    force_unlock_reason = fields.Text(
        string='Unlock Reason',
        copy=False,
    )
    force_unlock_date = fields.Datetime(
        string='Force Unlock Date',
        copy=False,
    )
    force_unlock_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Unlocked By',
        copy=False,
    )

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name, company_id)',
         'Reference must be unique per company!'),
    ]

    @api.depends('line_ids.price')
    def _compute_amount_total(self):
        for order in self:
            order.amount_total = sum(order.line_ids.mapped('price'))

    @api.depends('line_ids.image_ids')
    def _compute_total_image_count(self):
        for order in self:
            order.total_image_count = sum(order.line_ids.mapped('image_count'))

    def _compute_blocking_days(self):
        blocking_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'jewelry.blocking_days', default=14
        ))
        for order in self:
            order.blocking_days = blocking_days

    @api.depends('date', 'state')
    def _compute_blocking_end_date(self):
        blocking_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'jewelry.blocking_days', default=14
        ))
        for order in self:
            if order.date and order.state in ('confirmed', 'blocked', 'available', 'processed'):
                order.blocking_end_date = order.date + timedelta(days=blocking_days)
            else:
                order.blocking_end_date = False

    def _compute_days_remaining(self):
        today = fields.Date.today()
        for order in self:
            if order.blocking_end_date and order.state in ('confirmed', 'blocked'):
                delta = order.blocking_end_date - today
                order.days_remaining = max(0, delta.days)
            else:
                order.days_remaining = 0

    def _compute_can_process(self):
        today = fields.Date.today()
        for order in self:
            order.can_process = (
                order.state in ('blocked', 'available') and
                order.blocking_end_date and
                today >= order.blocking_end_date
            )

    @api.depends('line_ids.line_state')
    def _compute_all_lines_processed(self):
        for order in self:
            order.all_lines_processed = (
                order.line_ids and
                all(line.line_state != 'pending' for line in order.line_ids)
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'jewelry.client.purchase'
                ) or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError('Cannot confirm an order without lines.')
            if order.state != 'draft':
                raise UserError('Only draft orders can be confirmed.')
            order.write({'state': 'blocked'})
        return True

    def action_mark_available(self):
        for order in self:
            if order.state != 'blocked':
                raise UserError('Only blocked orders can be marked as available.')
            if not order.can_process:
                raise UserError(
                    f'Blocking period has not ended. {order.days_remaining} days remaining.'
                )
            order.write({'state': 'available'})
        return True

    def action_process(self):
        """Mark order as processed. All lines must be processed first.

        This method is called automatically when all lines are processed
        (in_inventory or to_smelting). Manual invocation requires all lines
        to have a final state.
        """
        for order in self:
            if order.state != 'available':
                raise UserError('Only available orders can be processed.')
            pending = order.line_ids.filtered(lambda l: l.line_state == 'pending')
            if pending:
                raise UserError(
                    f'Cannot process order. {len(pending)} line(s) are still pending.\n'
                    'Send all items to inventory or smelting first.'
                )
            order.write({'state': 'processed'})
            order.message_post(
                body='Order processed. All items have been sent to inventory or smelting.',
                subject='Order Completed',
                message_type='notification',
            )
        return True

    def action_cancel(self):
        for order in self:
            if order.state == 'processed':
                raise UserError('Cannot cancel a processed order.')
            order.write({'state': 'cancelled'})
        return True

    def action_draft(self):
        for order in self:
            if order.state not in ('cancelled',):
                raise UserError('Only cancelled orders can be reset to draft.')
            order.write({'state': 'draft'})
        return True

    def action_open_force_unlock_wizard(self):
        """Open the force unlock wizard."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Force Unlock',
            'res_model': 'jewelry.force.unlock.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_id': self.id},
        }

    def action_open_smelt_all_wizard(self):
        """Open the smelt all items wizard."""
        self.ensure_one()
        if self.state != 'available':
            raise UserError('Order must be in Available state.')
        pending_count = len(self.line_ids.filtered(lambda l: l.line_state == 'pending'))
        if not pending_count:
            raise UserError('No pending items to send to smelting.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Smelt All Items',
            'res_model': 'jewelry.smelt.all.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_id': self.id},
        }

    def action_open_receive_all_wizard(self):
        """Open the receive all items wizard."""
        self.ensure_one()
        if self.state != 'available':
            raise UserError('Order must be in Available state.')
        pending_count = len(self.line_ids.filtered(lambda l: l.line_state == 'pending'))
        if not pending_count:
            raise UserError('No pending items to receive.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receive All Items',
            'res_model': 'jewelry.receive.all.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_id': self.id},
        }

    def cron_check_blocking_period(self):
        """Cron job to automatically mark orders as available when blocking ends."""
        today = fields.Date.today()
        blocked_orders = self.search([
            ('state', '=', 'blocked'),
            ('blocking_end_date', '<=', today),
        ])
        blocked_orders.write({'state': 'available'})
        return True
