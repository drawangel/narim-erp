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
    operation_type = fields.Selection(
        selection=[
            ('purchase', 'Compra'),
            ('recoverable', 'Empeño'),
        ],
        string='Tipo de Operación',
        default='purchase',
        required=True,
        tracking=True,
        help='Compra: venta definitiva. Empeño: cliente puede recuperar pagando.',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Client',
        required=True,
        tracking=True,
        domain="[('is_company', '=', False)]",
        help='Individual client selling gold/jewelry',
    )
    partner_category_ids = fields.Many2many(
        related='partner_id.category_id',
        string='Etiquetas',
        readonly=True,
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
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Tienda',
        default=lambda self: self._get_default_warehouse(),
        check_company=True,
        tracking=True,
        help='Tienda donde se realiza la compra al particular',
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
            ('draft', 'Borrador'),
            ('blocked', 'Bloqueo Policial'),
            ('recoverable', 'Recuperable'),
            ('available', 'Disponible'),
            ('processed', 'Procesado'),
            ('recovered', 'Recuperado'),
            ('cancelled', 'Cancelado'),
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

    # Payment fields
    payment_method = fields.Selection(
        selection=[
            ('cash', 'Efectivo'),
            ('transfer', 'Transferencia Bancaria'),
            ('bizum', 'Bizum'),
            ('paypal', 'PayPal'),
            ('stripe', 'Stripe'),
            ('card', 'Tarjeta'),
        ],
        string='Forma de Pago',
        required=True,
        default='cash',
        tracking=True,
    )
    payment_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de Pago',
        domain="[('type', 'in', ['cash', 'bank'])]",
        help='Diario contable donde se registrará el pago',
    )
    payment_reference = fields.Char(
        string='Referencia de Pago',
        help='Número de transferencia, cheque, etc.',
        tracking=True,
    )
    partner_bank_iban = fields.Char(
        string='IBAN del Cliente',
        tracking=True,
        help='Número de cuenta IBAN donde realizar la transferencia al cliente',
    )

    # POS Integration fields
    pos_session_id = fields.Many2one(
        comodel_name='pos.session',
        string='Sesión de Caja',
        readonly=True,
        copy=False,
        help='Sesión POS donde se registró el movimiento de caja',
    )
    pos_statement_line_id = fields.Many2one(
        comodel_name='account.bank.statement.line',
        string='Movimiento de Caja',
        readonly=True,
        copy=False,
        help='Movimiento de caja generado en la sesión POS',
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

    # =====================================================
    # Pawn (Recoverable) Fields - Solo para empeños
    # =====================================================
    recovery_margin_percent = fields.Float(
        string='Margen Recuperación (%)',
        default=0.10,
        digits=(5, 2),
        help='Porcentaje sobre el precio de compra para calcular el precio de recuperación base',
    )
    recovery_deadline = fields.Date(
        string='Fecha Límite Recuperación',
        compute='_compute_recovery_deadline',
        store=True,
        help='Fecha hasta la que el cliente puede recuperar sin recargo diario adicional',
    )
    recovery_days = fields.Integer(
        string='Días para Recuperar',
        default=30,
        help='Número de días desde confirmación para recuperar sin recargo extra',
    )
    recovery_deadline_preview = fields.Date(
        string='Fecha Límite Estimada',
        compute='_compute_recovery_deadline_preview',
        help='Vista previa de la fecha límite de recuperación (basada en fecha de compra + días)',
    )
    daily_surcharge_percent = fields.Float(
        string='Recargo Diario (%)',
        default=0.10,
        digits=(5, 3),
        help='Porcentaje diario sobre el precio de compra si recupera después del plazo',
    )

    # Recovery amounts - editables para permitir ajustes manuales
    recovery_base_amount = fields.Monetary(
        string='Importe Recuperación',
        store=True,
        compute='_compute_recovery_base_amount',
        readonly=False,
        help='Precio compra + margen. Editable para ajustar el precio de recuperación.',
    )
    days_overdue = fields.Integer(
        string='Días Vencido',
        compute='_compute_days_overdue',
        help='Días transcurridos después de la fecha límite',
    )
    current_surcharge = fields.Monetary(
        string='Recargo por Demora',
        store=True,
        compute='_compute_current_surcharge',
        readonly=False,
        help='Recargo acumulado por demora. Editable para perdonar parcial o totalmente.',
    )
    total_recovery_amount = fields.Monetary(
        string='Total a Pagar',
        compute='_compute_total_recovery_amount',
        store=True,
        help='Suma de importe recuperación + recargo por mora',
    )
    can_recover = fields.Boolean(
        string='Puede Recuperar',
        compute='_compute_can_recover',
        help='True si el cliente puede recuperar (estado recoverable o available)',
    )

    # Recovery audit fields
    recovery_date = fields.Datetime(
        string='Fecha de Recuperación',
        copy=False,
    )
    recovery_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Recuperado por',
        copy=False,
    )
    recovery_amount_paid = fields.Monetary(
        string='Importe Pagado en Recuperación',
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
            if order.date and order.state not in ('draft', 'cancelled'):
                order.blocking_end_date = order.date + timedelta(days=blocking_days)
            else:
                order.blocking_end_date = False

    def _compute_days_remaining(self):
        today = fields.Date.today()
        for order in self:
            if order.blocking_end_date and order.state == 'blocked':
                delta = order.blocking_end_date - today
                order.days_remaining = max(0, delta.days)
            else:
                order.days_remaining = 0

    def _compute_can_process(self):
        today = fields.Date.today()
        for order in self:
            order.can_process = (
                order.state in ('blocked', 'available', 'recoverable') and
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

    # =====================================================
    # Pawn (Recovery) Computed Fields
    # =====================================================

    @api.depends('date', 'recovery_days', 'state', 'operation_type')
    def _compute_recovery_deadline(self):
        """Calcula la fecha límite de recuperación para empeños."""
        for order in self:
            if (order.operation_type == 'recoverable' and
                    order.date and
                    order.state not in ('draft', 'cancelled')):
                order.recovery_deadline = order.date + timedelta(days=order.recovery_days)
            else:
                order.recovery_deadline = False

    @api.depends('date', 'recovery_days', 'operation_type')
    def _compute_recovery_deadline_preview(self):
        """Vista previa de la fecha límite (visible en borrador)."""
        for order in self:
            if order.operation_type == 'recoverable' and order.date:
                order.recovery_deadline_preview = order.date + timedelta(days=order.recovery_days)
            else:
                order.recovery_deadline_preview = False

    @api.depends('amount_total', 'recovery_margin_percent', 'operation_type')
    def _compute_recovery_base_amount(self):
        """Calcula el importe base de recuperación (precio + margen).

        Este campo es editable (readonly=False) para permitir ajustes manuales.
        No recalcula si ya hay un valor guardado (para preservar ediciones manuales).
        """
        for order in self:
            if order.operation_type != 'recoverable':
                order.recovery_base_amount = 0
            elif not order.recovery_base_amount:
                # Solo calcular si no hay valor previo
                margin = order.amount_total * order.recovery_margin_percent
                order.recovery_base_amount = order.amount_total + margin

    @api.depends('recovery_deadline')
    def _compute_days_overdue(self):
        """Calcula los días vencidos después de la fecha límite."""
        today = fields.Date.today()
        for order in self:
            if order.recovery_deadline and today > order.recovery_deadline:
                order.days_overdue = (today - order.recovery_deadline).days
            else:
                order.days_overdue = 0

    @api.depends('amount_total', 'daily_surcharge_percent', 'days_overdue', 'operation_type')
    def _compute_current_surcharge(self):
        """Calcula el recargo por demora.

        Este campo es editable (readonly=False) para permitir perdonar
        parcial o totalmente el recargo.
        Solo recalcula si days_overdue > 0 y no hay valor previo guardado.
        """
        for order in self:
            if order.operation_type != 'recoverable':
                order.current_surcharge = 0
            elif order.days_overdue <= 0:
                # Sin demora, no hay recargo (pero respetamos si ya hay valor manual)
                if not order.id:  # Solo en creación
                    order.current_surcharge = 0
            # Si hay días vencidos y no hay valor previo, calcular
            elif order.days_overdue > 0 and not order.current_surcharge:
                order.current_surcharge = (
                    order.amount_total * order.daily_surcharge_percent * order.days_overdue
                )

    @api.depends('recovery_base_amount', 'current_surcharge')
    def _compute_total_recovery_amount(self):
        """Calcula el total a pagar (importe recuperación + recargo)."""
        for order in self:
            order.total_recovery_amount = order.recovery_base_amount + order.current_surcharge

    @api.depends('operation_type', 'state')
    def _compute_can_recover(self):
        """Determina si el cliente puede recuperar el empeño."""
        for order in self:
            order.can_recover = (
                order.operation_type == 'recoverable' and
                order.state in ('blocked', 'recoverable', 'available')
            )

    @api.model
    def _get_default_warehouse(self):
        """Obtiene el almacén por defecto del usuario o el primero de la compañía."""
        # Primero intenta el warehouse del usuario (si tiene sale_stock instalado)
        if hasattr(self.env.user, '_get_default_warehouse_id'):
            warehouse = self.env.user._get_default_warehouse_id()
            if warehouse:
                return warehouse
        # Fallback: primer warehouse de la compañía
        return self.env['stock.warehouse'].search(
            [('company_id', '=', self.env.company.id)],
            limit=1
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'jewelry.client.purchase'
                ) or 'New'
        return super().create(vals_list)

    # =====================================================
    # POS Integration Methods
    # =====================================================

    def _get_active_pos_session(self):
        """Get the open POS session for the current store/company."""
        self.ensure_one()
        # Search for POS config associated with the company
        pos_config = self.env['pos.config'].search([
            ('company_id', '=', self.company_id.id),
        ], limit=1)

        if not pos_config:
            return False

        session = self.env['pos.session'].search([
            ('config_id', '=', pos_config.id),
            ('state', '=', 'opened'),
        ], limit=1)

        return session

    def _create_pos_cash_out(self):
        """Create a cash out movement in the active POS session."""
        self.ensure_one()

        if self.payment_method != 'cash':
            return False

        session = self._get_active_pos_session()
        if not session:
            raise UserError(
                'No hay sesión de caja abierta.\n'
                'Abra una sesión POS antes de confirmar compras en efectivo.'
            )

        if not session.cash_journal_id:
            raise UserError(
                'La sesión POS no tiene un diario de efectivo configurado.'
            )

        # Create cash out movement
        reason = f'Compra cliente: {self.name}'

        # Prepare statement line values (amount negative for cash out)
        vals = {
            'pos_session_id': session.id,
            'journal_id': session.cash_journal_id.id,
            'amount': -self.amount_total,  # Negative for cash out
            'date': fields.Date.context_today(self),
            'payment_ref': f'{session.name}-out-{reason}',
        }
        statement_line = self.env['account.bank.statement.line'].create(vals)

        # Save references
        self.write({
            'pos_session_id': session.id,
            'pos_statement_line_id': statement_line.id,
        })

        self.message_post(
            body=f'Salida de caja registrada: {self.amount_total} € en sesión {session.name}',
            message_type='notification',
        )

        return statement_line

    def _create_pos_cash_reversal(self):
        """Create a reversal cash in movement in the POS session."""
        self.ensure_one()
        session = self.pos_session_id

        if not session:
            return False

        if session.state != 'opened':
            raise UserError(
                'La sesión de caja no está abierta. '
                'No se puede revertir el movimiento de caja.'
            )

        # Create cash in (reversal) - positive amount
        reason = f'ANULACIÓN Compra: {self.name}'
        vals = {
            'pos_session_id': session.id,
            'journal_id': session.cash_journal_id.id,
            'amount': self.amount_total,  # Positive for cash in (reversal)
            'date': fields.Date.context_today(self),
            'payment_ref': f'{session.name}-in-{reason}',
        }
        self.env['account.bank.statement.line'].create(vals)

        self.message_post(
            body=f'Movimiento de caja revertido: {self.amount_total} € (entrada)',
            message_type='notification',
        )

    # =====================================================
    # Action Methods
    # =====================================================

    def action_confirm(self):
        for order in self:
            if not order.line_ids:
                raise UserError('Cannot confirm an order without lines.')
            if order.state != 'draft':
                raise UserError('Only draft orders can be confirmed.')

            # Register cash out in POS session if payment is cash
            if order.payment_method == 'cash':
                order._create_pos_cash_out()

            order.write({'state': 'blocked'})
        return True

    def action_mark_available(self):
        """Marca como disponible cuando el bloqueo termina.

        Para compras normales: permite enviar a inventario/fundición.
        Para empeños: indica que el plazo de recuperación venció.
        """
        for order in self:
            if order.state not in ('blocked', 'recoverable'):
                raise UserError('Solo órdenes en bloqueo o recuperables pueden marcarse como disponibles.')
            if order.state == 'blocked' and not order.can_process:
                raise UserError(
                    f'El período de bloqueo no ha terminado. Faltan {order.days_remaining} días.'
                )
            order.write({'state': 'available'})
        return True

    def action_mark_recoverable(self):
        """Marca un empeño como recuperable tras el bloqueo policial.

        Solo aplica a empeños que aún están en plazo de recuperación.
        """
        for order in self:
            if order.operation_type != 'recoverable':
                raise UserError('Solo los empeños pueden marcarse como recuperables.')
            if order.state != 'blocked':
                raise UserError('Solo órdenes en bloqueo pueden marcarse como recuperables.')
            if not order.can_process:
                raise UserError(
                    f'El período de bloqueo no ha terminado. Faltan {order.days_remaining} días.'
                )
            order.write({'state': 'recoverable'})
        return True

    def action_process(self):
        """Mark order as processed. All lines must be processed first.

        This method is called automatically when all lines are processed
        (in_inventory or to_smelting). Manual invocation requires all lines
        to have a final state.
        """
        for order in self:
            if order.state != 'available':
                raise UserError('Solo órdenes disponibles pueden procesarse.')
            pending = order.line_ids.filtered(lambda l: l.line_state == 'pending')
            if pending:
                raise UserError(
                    f'No se puede procesar. {len(pending)} línea(s) aún pendientes.\n'
                    'Envíe todos los artículos a inventario o fundición primero.'
                )
            order.write({'state': 'processed'})
            order.message_post(
                body='Orden procesada. Todos los artículos han sido enviados a inventario o fundición.',
                subject='Orden Completada',
                message_type='notification',
            )
        return True

    def action_cancel(self):
        for order in self:
            if order.state in ('processed', 'recovered'):
                raise UserError('No se puede cancelar una orden procesada o recuperada.')

            # Revert cash movement if exists and session is still open
            if order.pos_statement_line_id and order.pos_session_id:
                if order.pos_session_id.state == 'closed':
                    raise UserError(
                        'No se puede cancelar: la sesión de caja ya está cerrada.\n'
                        'Contacte al administrador para realizar un ajuste manual.'
                    )
                order._create_pos_cash_reversal()

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
        """Cron job: procesa transiciones automáticas de estado.

        Transiciones:
        1. Compras normales: blocked → available (cuando bloqueo termina)
        2. Empeños en bloqueo: blocked → recoverable (cuando bloqueo termina y aún en plazo)
        3. Empeños recuperables: recoverable → available (cuando plazo de recuperación vence)
        """
        today = fields.Date.today()

        # 1. Compras normales: blocked → available
        blocked_purchases = self.search([
            ('state', '=', 'blocked'),
            ('operation_type', '=', 'purchase'),
            ('blocking_end_date', '<=', today),
        ])
        if blocked_purchases:
            blocked_purchases.write({'state': 'available'})
            for order in blocked_purchases:
                order.message_post(
                    body='Período de bloqueo finalizado. Artículos disponibles para procesar.',
                    message_type='notification',
                )

        # 2. Empeños: blocked → recoverable (bloqueo terminó pero plazo aún vigente)
        blocked_pawns = self.search([
            ('state', '=', 'blocked'),
            ('operation_type', '=', 'recoverable'),
            ('blocking_end_date', '<=', today),
            ('recovery_deadline', '>', today),
        ])
        if blocked_pawns:
            blocked_pawns.write({'state': 'recoverable'})
            for order in blocked_pawns:
                order.message_post(
                    body=f'Período de bloqueo finalizado. Cliente puede recuperar hasta {order.recovery_deadline}.',
                    message_type='notification',
                )

        # 3. Empeños: blocked → available (bloqueo terminó y plazo también venció)
        blocked_pawns_expired = self.search([
            ('state', '=', 'blocked'),
            ('operation_type', '=', 'recoverable'),
            ('blocking_end_date', '<=', today),
            ('recovery_deadline', '<=', today),
        ])
        if blocked_pawns_expired:
            blocked_pawns_expired.write({'state': 'available'})
            for order in blocked_pawns_expired:
                order.message_post(
                    body='Período de bloqueo y plazo de recuperación finalizados. Artículos disponibles para procesar.',
                    message_type='notification',
                )

        # 4. Empeños recuperables: recoverable → available (plazo venció)
        expired_pawns = self.search([
            ('state', '=', 'recoverable'),
            ('operation_type', '=', 'recoverable'),
            ('recovery_deadline', '<=', today),
        ])
        if expired_pawns:
            expired_pawns.write({'state': 'available'})
            for order in expired_pawns:
                order.message_post(
                    body='Plazo de recuperación vencido. Artículos disponibles para procesar.',
                    message_type='notification',
                )

        return True

    def action_open_recovery_wizard(self):
        """Abre el wizard de recuperación para empeños."""
        self.ensure_one()
        if self.operation_type != 'recoverable':
            raise UserError('Solo los empeños pueden recuperarse.')
        if not self.can_recover:
            raise UserError('Este empeño no puede recuperarse en su estado actual.')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recuperar Empeño',
            'res_model': 'jewelry.recovery.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_id': self.id},
        }

    def action_recover(self, amount_paid):
        """Marca el empeño como recuperado.

        Este método es llamado desde el wizard de recuperación.
        """
        self.ensure_one()
        if self.operation_type != 'recoverable':
            raise UserError('Solo los empeños pueden recuperarse.')
        if not self.can_recover:
            raise UserError('Este empeño no puede recuperarse en su estado actual.')

        self.write({
            'state': 'recovered',
            'recovery_date': fields.Datetime.now(),
            'recovery_user_id': self.env.user.id,
            'recovery_amount_paid': amount_paid,
        })

        self.message_post(
            body=(
                f'Empeño recuperado por el cliente.<br/>'
                f'<b>Importe pagado:</b> {amount_paid} {self.currency_id.symbol}<br/>'
                f'<b>Registrado por:</b> {self.env.user.name}'
            ),
            subject='Empeño Recuperado',
            message_type='notification',
        )
        return True
