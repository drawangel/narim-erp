from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = 'pos.session'

    client_purchase_ids = fields.One2many(
        comodel_name='jewelry.client.purchase',
        inverse_name='pos_session_id',
        string='Compras a Clientes',
        readonly=True,
    )

    client_purchase_count = fields.Integer(
        string='Compras a Clientes',
        compute='_compute_client_purchase_stats',
    )

    client_purchase_total = fields.Monetary(
        string='Total Compras a Clientes',
        compute='_compute_client_purchase_stats',
    )

    @api.depends('client_purchase_ids.amount_total', 'client_purchase_ids.state')
    def _compute_client_purchase_stats(self):
        for session in self:
            purchases = session.client_purchase_ids.filtered(
                lambda p: p.state not in ('cancelled', 'draft')
            )
            session.client_purchase_count = len(purchases)
            session.client_purchase_total = sum(purchases.mapped('amount_total'))

    def action_view_client_purchases(self):
        """Open client purchases linked to this session."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compras a Clientes',
            'res_model': 'jewelry.client.purchase',
            'view_mode': 'list,form',
            'domain': [('pos_session_id', '=', self.id)],
            'context': {'default_pos_session_id': self.id},
        }
