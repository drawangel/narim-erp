# Modelo de Datos - Sistema de Compraventa

## Modelo Principal: `jewelry.client.purchase`

### Campos Existentes (ya implementados)

```python
# Identificación
name = fields.Char('Reference', required=True, readonly=True, default='New')
partner_id = fields.Many2one('res.partner', 'Client', required=True)
date = fields.Date('Date', required=True, default=fields.Date.today)
company_id = fields.Many2one('res.company', required=True)
user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
currency_id = fields.Many2one('res.currency', required=True)

# Líneas y totales
line_ids = fields.One2many('jewelry.client.purchase.line', 'order_id')
amount_total = fields.Monetary(compute='_compute_amount_total', store=True)

# Estado actual (a modificar)
state = fields.Selection([...], default='draft')

# Pago
payment_method = fields.Selection([...], default='cash')
payment_journal_id = fields.Many2one('account.journal')
payment_reference = fields.Char('Payment Reference')

# Integración POS
pos_session_id = fields.Many2one('pos.session', readonly=True)
pos_statement_line_id = fields.Many2one('account.bank.statement.line', readonly=True)

# Bloqueo policial
blocking_days = fields.Integer(compute='_compute_blocking_days')
blocking_end_date = fields.Date(compute='_compute_blocking_end_date', store=True)
days_remaining = fields.Integer(compute='_compute_days_remaining')
can_process = fields.Boolean(compute='_compute_can_process')

# Desbloqueo forzado (auditoría)
force_unlocked = fields.Boolean(default=False)
force_unlock_reason = fields.Text()
force_unlock_date = fields.Datetime()
force_unlock_user_id = fields.Many2one('res.users')

# Otros
notes = fields.Text('Internal Notes')
total_image_count = fields.Integer(compute='_compute_total_image_count')
all_lines_processed = fields.Boolean(compute='_compute_all_lines_processed', store=True)
```

### Campos Nuevos (a implementar)

#### 1. Tipo de Operación

```python
operation_type = fields.Selection(
    selection=[
        ('purchase', 'Compra'),
        ('recoverable', 'Recuperable'),
    ],
    string='Tipo de Operación',
    default='purchase',
    required=True,
    tracking=True,
    help='Compra: venta definitiva. Recuperable: el cliente puede recuperar.',
)
```

#### 2. Estado Actualizado

```python
state = fields.Selection(
    selection=[
        ('draft', 'Borrador'),
        ('blocked', 'Bloqueo Policial'),
        ('recoverable', 'Recuperable'),      # NUEVO
        ('available', 'Disponible'),
        ('to_smelt', 'A Fundir'),             # NUEVO (antes era estado de línea)
        ('inventory', 'Inventario'),          # NUEVO (antes era estado de línea)
        ('smelted', 'Fundido'),               # NUEVO
        ('recovered', 'Recuperado'),          # NUEVO
        ('sold', 'Venta'),                    # NUEVO
        ('cancelled', 'Cancelado'),
    ],
    string='Estado',
    default='draft',
    required=True,
    tracking=True,
    index=True,
)
```

#### 3. Campos de Recuperación (Empeño)

```python
# Condiciones del empeño
recovery_margin_percent = fields.Float(
    string='Margen Recuperación (%)',
    digits=(5, 2),
    default=lambda self: float(self.env['ir.config_parameter'].sudo().get_param(
        'jewelry.default_margin', default=20.0
    )),
    help='Porcentaje sobre el precio de compra para recuperación',
)
recovery_deadline = fields.Date(
    string='Fecha Límite Recuperación',
    help='Fecha hasta la que el cliente puede recuperar sin recargo',
)
recovery_duration_days = fields.Integer(
    string='Días de Empeño',
    help='Número de días que dura el empeño desde la fecha de compra',
)
daily_surcharge_percent = fields.Float(
    string='Recargo Diario (%)',
    digits=(5, 2),
    default=lambda self: float(self.env['ir.config_parameter'].sudo().get_param(
        'jewelry.default_surcharge', default=0.5
    )),
    help='Porcentaje diario sobre el precio de compra si recupera después del plazo',
)

# Campos calculados
recovery_base_amount = fields.Monetary(
    string='Importe Recuperación Base',
    compute='_compute_recovery_amounts',
    store=True,
    help='Precio compra + margen (sin recargo)',
)
days_overdue = fields.Integer(
    string='Días Vencido',
    compute='_compute_recovery_amounts',
    help='Días transcurridos desde la fecha límite',
)
current_surcharge = fields.Monetary(
    string='Recargo Actual',
    compute='_compute_recovery_amounts',
    help='Recargo acumulado por días vencidos',
)
total_recovery_amount = fields.Monetary(
    string='Total a Pagar Hoy',
    compute='_compute_recovery_amounts',
    help='Importe total que debe pagar el cliente para recuperar',
)
can_recover = fields.Boolean(
    string='Puede Recuperar',
    compute='_compute_can_recover',
    help='True si el cliente puede recuperar en el estado actual',
)

# Datos de recuperación (cuando se ejecuta)
recovery_date = fields.Datetime(
    string='Fecha Recuperación',
    readonly=True,
    copy=False,
)
recovery_user_id = fields.Many2one(
    comodel_name='res.users',
    string='Recuperado Por',
    readonly=True,
    copy=False,
)
recovery_amount_paid = fields.Monetary(
    string='Importe Pagado en Recuperación',
    readonly=True,
    copy=False,
)
recovery_pos_statement_line_id = fields.Many2one(
    comodel_name='account.bank.statement.line',
    string='Movimiento Caja (Recuperación)',
    readonly=True,
    copy=False,
)
```

### Métodos Computed Nuevos

```python
@api.depends('date', 'recovery_duration_days')
def _compute_recovery_deadline(self):
    """Calcula la fecha límite de recuperación."""
    for order in self:
        if order.date and order.recovery_duration_days:
            order.recovery_deadline = order.date + timedelta(days=order.recovery_duration_days)
        else:
            order.recovery_deadline = False

@api.depends('amount_total', 'recovery_margin_percent', 'daily_surcharge_percent',
             'recovery_deadline', 'state')
def _compute_recovery_amounts(self):
    """Calcula los importes de recuperación."""
    today = fields.Date.today()
    for order in self:
        if order.operation_type != 'recoverable':
            order.recovery_base_amount = 0
            order.days_overdue = 0
            order.current_surcharge = 0
            order.total_recovery_amount = 0
            continue

        # Importe base: precio + margen
        margin = order.amount_total * (order.recovery_margin_percent / 100)
        order.recovery_base_amount = order.amount_total + margin

        # Calcular días vencido y recargo
        if order.recovery_deadline and today > order.recovery_deadline:
            order.days_overdue = (today - order.recovery_deadline).days
            order.current_surcharge = (
                order.amount_total *
                (order.daily_surcharge_percent / 100) *
                order.days_overdue
            )
        else:
            order.days_overdue = 0
            order.current_surcharge = 0

        order.total_recovery_amount = order.recovery_base_amount + order.current_surcharge

@api.depends('state', 'operation_type')
def _compute_can_recover(self):
    """Determina si el cliente puede recuperar en el estado actual."""
    for order in self:
        order.can_recover = (
            order.operation_type == 'recoverable' and
            order.state in ('blocked', 'recoverable', 'available')
        )
```

### Métodos de Acción Nuevos

```python
def action_recover(self):
    """Cliente recupera el artículo pagando el importe correspondiente."""
    self.ensure_one()
    if not self.can_recover:
        raise UserError('No se puede recuperar en el estado actual.')

    # Abrir wizard de recuperación para confirmar importe y método de pago
    return {
        'type': 'ir.actions.act_window',
        'name': 'Recuperación de Empeño',
        'res_model': 'jewelry.recovery.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {
            'default_purchase_id': self.id,
            'default_recovery_amount': self.total_recovery_amount,
        },
    }

def _execute_recovery(self, payment_method='cash'):
    """Ejecuta la recuperación (llamado desde el wizard)."""
    self.ensure_one()

    # Registrar entrada de caja si es efectivo
    statement_line = False
    if payment_method == 'cash':
        statement_line = self._create_recovery_cash_in()

    self.write({
        'state': 'recovered',
        'recovery_date': fields.Datetime.now(),
        'recovery_user_id': self.env.user.id,
        'recovery_amount_paid': self.total_recovery_amount,
        'recovery_pos_statement_line_id': statement_line.id if statement_line else False,
    })

    self.message_post(
        body=f'Cliente recuperó el empeño. Importe cobrado: {self.total_recovery_amount} €',
        subject='Empeño Recuperado',
        message_type='notification',
    )

def _create_recovery_cash_in(self):
    """Crea entrada de caja para la recuperación."""
    self.ensure_one()
    session = self._get_active_pos_session()
    if not session:
        raise UserError('No hay sesión de caja abierta.')

    vals = {
        'pos_session_id': session.id,
        'journal_id': session.cash_journal_id.id,
        'amount': self.total_recovery_amount,  # Positivo: entrada
        'date': fields.Date.context_today(self),
        'payment_ref': f'{session.name}-in-Recuperación: {self.name}',
    }
    return self.env['account.bank.statement.line'].create(vals)
```

---

## Modelo de Líneas: `jewelry.client.purchase.line`

### Campos Existentes

Los campos de línea se mantienen sin cambios significativos. El estado de línea (`line_state`) se simplifica ya que el estado principal ahora está en la orden.

### Cambios Menores

```python
# El campo line_state podría simplificarse o eliminarse
# ya que el estado principal está en el pedido
line_state = fields.Selection(
    selection=[
        ('pending', 'Pendiente'),
        ('processed', 'Procesado'),
    ],
    string='Estado Línea',
    default='pending',
    help='Estado de procesamiento de esta línea',
)
```

---

## Wizard de Recuperación (NUEVO)

### Modelo: `jewelry.recovery.wizard`

```python
class RecoveryWizard(models.TransientModel):
    _name = 'jewelry.recovery.wizard'
    _description = 'Wizard de Recuperación de Empeño'

    purchase_id = fields.Many2one(
        comodel_name='jewelry.client.purchase',
        string='Compra',
        required=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='purchase_id.partner_id',
        string='Cliente',
    )

    # Montos (readonly, informativos)
    purchase_amount = fields.Monetary(
        related='purchase_id.amount_total',
        string='Importe Original',
    )
    recovery_base = fields.Monetary(
        related='purchase_id.recovery_base_amount',
        string='Base (precio + margen)',
    )
    surcharge = fields.Monetary(
        related='purchase_id.current_surcharge',
        string='Recargo',
    )
    recovery_amount = fields.Monetary(
        string='Total a Cobrar',
        required=True,
    )
    currency_id = fields.Many2one(
        related='purchase_id.currency_id',
    )

    # Método de pago
    payment_method = fields.Selection(
        selection=[
            ('cash', 'Efectivo'),
            ('transfer', 'Transferencia'),
            ('card', 'Tarjeta'),
        ],
        string='Método de Pago',
        default='cash',
        required=True,
    )

    def action_confirm_recovery(self):
        """Confirma la recuperación."""
        self.ensure_one()
        self.purchase_id._execute_recovery(payment_method=self.payment_method)
        return {'type': 'ir.actions.act_window_close'}
```

---

## Parámetros de Configuración

### Nuevos Parámetros en `res.config.settings`

```python
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Ya existente
    jewelry_blocking_days = fields.Integer(
        string='Días de Bloqueo Legal',
        config_parameter='jewelry.blocking_days',
        default=14,
    )

    # Nuevos para empeños
    jewelry_default_margin = fields.Float(
        string='Margen por Defecto (%)',
        config_parameter='jewelry.default_margin',
        default=20.0,
        help='Margen aplicado por defecto en compras recuperables',
    )
    jewelry_default_surcharge = fields.Float(
        string='Recargo Diario por Defecto (%)',
        config_parameter='jewelry.default_surcharge',
        default=0.5,
        help='Recargo diario aplicado por defecto tras vencer el plazo',
    )
    jewelry_default_recovery_days = fields.Integer(
        string='Días de Empeño por Defecto',
        config_parameter='jewelry.default_recovery_days',
        default=30,
        help='Duración por defecto de un empeño en días',
    )
```

---

## Migración de Datos

Al implementar estos cambios, se requiere una migración para:

1. Añadir `operation_type = 'purchase'` a todos los registros existentes
2. Mapear estados antiguos a nuevos:
   - `confirmed` → `blocked` (si aún en bloqueo)
   - `processed` → determinar según `line_state` de las líneas

```python
def migrate(cr, version):
    """Migración de datos para nuevos estados."""
    # Establecer tipo de operación por defecto
    cr.execute("""
        UPDATE jewelry_client_purchase
        SET operation_type = 'purchase'
        WHERE operation_type IS NULL
    """)

    # Mapear estado 'confirmed' a 'blocked'
    cr.execute("""
        UPDATE jewelry_client_purchase
        SET state = 'blocked'
        WHERE state = 'confirmed'
    """)
```
