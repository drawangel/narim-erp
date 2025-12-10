import base64

from odoo import api, fields, models
from odoo.exceptions import UserError


class PoliceReportWizard(models.TransientModel):
    _name = 'jewelry.report.police.wizard'
    _description = 'Generador de Informe Policial'

    # Date range
    date_from = fields.Date(
        string='Desde',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
    )
    date_to = fields.Date(
        string='Hasta',
        required=True,
        default=fields.Date.today,
    )

    # State filters (multiple selection via booleans)
    include_blocked = fields.Boolean(
        string='Bloqueo Policial',
        default=True,
    )
    include_recoverable = fields.Boolean(
        string='Recuperable',
        default=True,
    )
    include_available = fields.Boolean(
        string='Disponible',
        default=True,
    )
    include_processed = fields.Boolean(
        string='Procesado',
        default=True,
    )
    include_recovered = fields.Boolean(
        string='Recuperado',
        default=False,
    )

    # Store filter
    warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        string='Tiendas',
        help='Dejar vacío para incluir todas las tiendas',
    )

    # Operation type filter
    operation_type = fields.Selection(
        selection=[
            ('all', 'Todos'),
            ('purchase', 'Solo Compras'),
            ('recoverable', 'Solo Empeños'),
        ],
        string='Tipo de Operación',
        default='all',
    )

    # Output format
    output_format = fields.Selection(
        selection=[
            ('excel', 'Excel (.xlsx)'),
            ('pdf', 'PDF'),
        ],
        string='Formato',
        default='excel',
        required=True,
    )

    # Generated file (for download)
    file_data = fields.Binary(
        string='Archivo',
        readonly=True,
    )
    file_name = fields.Char(
        string='Nombre del Archivo',
        readonly=True,
    )

    # Preview count
    record_count = fields.Integer(
        string='Registros Encontrados',
        compute='_compute_record_count',
    )

    @api.depends('date_from', 'date_to', 'include_blocked', 'include_recoverable',
                 'include_available', 'include_processed', 'include_recovered',
                 'warehouse_ids', 'operation_type')
    def _compute_record_count(self):
        for wizard in self:
            lines = wizard._get_purchase_lines()
            wizard.record_count = len(lines)

    def _get_selected_states(self):
        """Return list of selected states based on boolean fields."""
        states = []
        if self.include_blocked:
            states.append('blocked')
        if self.include_recoverable:
            states.append('recoverable')
        if self.include_available:
            states.append('available')
        if self.include_processed:
            states.append('processed')
        if self.include_recovered:
            states.append('recovered')
        return states

    def _get_purchase_lines(self):
        """Get purchase lines matching the filter criteria."""
        self.ensure_one()

        states = self._get_selected_states()
        if not states:
            return self.env['jewelry.client.purchase.line'].browse()

        # Build domain
        domain = [
            ('order_id.date', '>=', self.date_from),
            ('order_id.date', '<=', self.date_to),
            ('order_id.state', 'in', states),
        ]

        # Warehouse filter
        if self.warehouse_ids:
            domain.append(('order_id.warehouse_id', 'in', self.warehouse_ids.ids))

        # Operation type filter
        if self.operation_type == 'purchase':
            domain.append(('order_id.operation_type', '=', 'purchase'))
        elif self.operation_type == 'recoverable':
            domain.append(('order_id.operation_type', '=', 'recoverable'))

        return self.env['jewelry.client.purchase.line'].search(
            domain,
            order='order_id, sequence, id',
        )

    def _prepare_excel_data(self, lines):
        """Prepare data rows for Excel export.

        Returns list of dicts with keys matching the required Excel columns.
        """
        data = []
        for line in lines:
            order = line.order_id
            partner = order.partner_id

            # Format date as DD/MM/YYYY
            date_str = order.date.strftime('%d/%m/%Y') if order.date else ''

            data.append({
                'contract_number': order.name or '',
                'client_name': partner.name or '',
                'dni': partner.vat or '',
                'purchase_date': date_str,
                'store': order.warehouse_id.name if order.warehouse_id else '',
                'jewelry_type': line.jewelry_type_id.name if line.jewelry_type_id else '',
                'description': line.description or '',
                'inscriptions': line.inscriptions or 'SN INSCRIPCIONS',
            })
        return data

    def action_generate(self):
        """Generate the police report in selected format."""
        self.ensure_one()

        lines = self._get_purchase_lines()
        if not lines:
            raise UserError('No se encontraron registros con los filtros seleccionados.')

        if self.output_format == 'excel':
            return self._generate_excel(lines)
        else:
            return self._generate_pdf(lines)

    def _generate_excel(self, lines):
        """Generate Excel file and return download action."""
        from ..report.police_report_excel import PoliceReportExcel

        data = self._prepare_excel_data(lines)
        generator = PoliceReportExcel()
        file_content = generator.generate(data)

        # Create filename with date range
        filename = f"informe_policial_{self.date_from}_{self.date_to}.xlsx"

        # Save file data
        self.write({
            'file_data': file_content,
            'file_name': filename,
        })

        # Return download action
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{self._name}/{self.id}/file_data/{filename}?download=true',
            'target': 'new',
        }

    def _generate_pdf(self, lines):
        """Generate PDF report and return download action."""
        import logging
        _logger = logging.getLogger(__name__)

        # Get unique purchases from lines
        purchases = lines.mapped('order_id')

        _logger.info(f"PDF Generation - Lines: {len(lines)}, Purchases: {purchases.ids}")

        if not purchases:
            raise UserError('No se encontraron compras para generar el PDF.')

        # Use standard report action
        return self.env.ref('jewelry_report.action_report_police_pdf').report_action(purchases)
