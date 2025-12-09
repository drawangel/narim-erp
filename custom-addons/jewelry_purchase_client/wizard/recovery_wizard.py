from odoo import api, fields, models
from odoo.exceptions import UserError


class RecoveryWizard(models.TransientModel):
    _name = 'jewelry.recovery.wizard'
    _description = 'Wizard de Recuperación de Empeño'

    purchase_id = fields.Many2one(
        comodel_name='jewelry.client.purchase',
        string='Empeño',
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='purchase_id.partner_id',
        string='Cliente',
    )
    currency_id = fields.Many2one(
        related='purchase_id.currency_id',
        string='Moneda',
    )

    # Información del empeño (readonly)
    purchase_date = fields.Date(
        related='purchase_id.date',
        string='Fecha de Compra',
    )
    original_amount = fields.Monetary(
        related='purchase_id.amount_total',
        string='Importe Original',
        currency_field='currency_id',
    )
    recovery_deadline = fields.Date(
        related='purchase_id.recovery_deadline',
        string='Fecha Límite',
    )
    recovery_margin_percent = fields.Float(
        related='purchase_id.recovery_margin_percent',
        string='Margen (%)',
    )
    daily_surcharge_percent = fields.Float(
        related='purchase_id.daily_surcharge_percent',
        string='Recargo Diario (%)',
    )

    # Cálculos de recuperación (editables para ajustar precios)
    recovery_base_amount = fields.Monetary(
        string='Importe Recuperación',
        currency_field='currency_id',
        help='Precio compra + margen. Editable para ajustar el importe.',
    )
    days_overdue = fields.Integer(
        related='purchase_id.days_overdue',
        string='Días Vencido',
    )
    current_surcharge = fields.Monetary(
        string='Recargo por Demora',
        currency_field='currency_id',
        help='Recargo acumulado. Editable para perdonar parcial o totalmente.',
    )
    total_recovery_amount = fields.Monetary(
        string='Total a Pagar',
        currency_field='currency_id',
        compute='_compute_total_recovery_amount',
    )

    # Campos editables
    amount_received = fields.Monetary(
        string='Importe Recibido',
        currency_field='currency_id',
        required=True,
        help='Importe que el cliente paga para recuperar el empeño',
    )
    payment_method = fields.Selection(
        selection=[
            ('cash', 'Efectivo'),
            ('transfer', 'Transferencia Bancaria'),
            ('bizum', 'Bizum'),
            ('card', 'Tarjeta'),
        ],
        string='Forma de Pago',
        default='cash',
        required=True,
    )
    notes = fields.Text(
        string='Notas',
        help='Observaciones sobre la recuperación',
    )

    @api.depends('recovery_base_amount', 'current_surcharge')
    def _compute_total_recovery_amount(self):
        for wizard in self:
            wizard.total_recovery_amount = wizard.recovery_base_amount + wizard.current_surcharge

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'purchase_id' in res:
            purchase = self.env['jewelry.client.purchase'].browse(res['purchase_id'])
            # Pre-llenar con los valores actuales del empeño
            res['recovery_base_amount'] = purchase.recovery_base_amount
            res['current_surcharge'] = purchase.current_surcharge
            res['amount_received'] = purchase.total_recovery_amount
        return res

    @api.onchange('purchase_id')
    def _onchange_purchase_id(self):
        if self.purchase_id:
            self.recovery_base_amount = self.purchase_id.recovery_base_amount
            self.current_surcharge = self.purchase_id.current_surcharge
            self.amount_received = self.purchase_id.total_recovery_amount

    @api.onchange('recovery_base_amount', 'current_surcharge')
    def _onchange_amounts(self):
        """Actualiza el importe a recibir cuando se modifican los importes."""
        self.amount_received = self.recovery_base_amount + self.current_surcharge

    def action_confirm_recovery(self):
        """Confirma la recuperación del empeño."""
        self.ensure_one()
        purchase = self.purchase_id

        if not purchase.can_recover:
            raise UserError('Este empeño no puede recuperarse en su estado actual.')

        if self.amount_received <= 0:
            raise UserError('El importe recibido debe ser mayor que cero.')

        # Validar que el importe recibido sea al menos el total calculado
        if self.amount_received < self.total_recovery_amount:
            raise UserError(
                f'El importe recibido ({self.amount_received:.2f}) es menor que el '
                f'total a pagar ({self.total_recovery_amount:.2f}).\n'
                'No se puede procesar la recuperación con un importe menor.'
            )

        # Guardar los importes ajustados en el empeño
        purchase.write({
            'recovery_base_amount': self.recovery_base_amount,
            'current_surcharge': self.current_surcharge,
        })

        # Registrar entrada de caja si es efectivo
        if self.payment_method == 'cash':
            self._create_pos_cash_in()

        # Marcar como recuperado
        purchase.action_recover(self.amount_received)

        # Agregar nota si existe
        if self.notes:
            purchase.message_post(
                body=f'<b>Notas de recuperación:</b><br/>{self.notes}',
                message_type='comment',
            )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Empeño Recuperado',
                'message': f'El cliente ha recuperado el empeño {purchase.name}.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def _create_pos_cash_in(self):
        """Crea una entrada de caja en la sesión POS activa."""
        self.ensure_one()
        purchase = self.purchase_id

        session = purchase._get_active_pos_session()
        if not session:
            raise UserError(
                'No hay sesión de caja abierta.\n'
                'Abra una sesión POS antes de registrar pagos en efectivo.'
            )

        if not session.cash_journal_id:
            raise UserError(
                'La sesión POS no tiene un diario de efectivo configurado.'
            )

        # Crear entrada de caja (amount positivo)
        reason = f'Recuperación empeño: {purchase.name}'
        vals = {
            'pos_session_id': session.id,
            'journal_id': session.cash_journal_id.id,
            'amount': self.amount_received,  # Positivo = entrada
            'date': fields.Date.context_today(self),
            'payment_ref': f'{session.name}-in-{reason}',
        }
        self.env['account.bank.statement.line'].create(vals)

        purchase.message_post(
            body=f'Entrada de caja registrada: {self.amount_received} € en sesión {session.name}',
            message_type='notification',
        )
