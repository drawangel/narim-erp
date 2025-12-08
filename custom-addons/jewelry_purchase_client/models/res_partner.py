from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    client_purchase_ids = fields.One2many(
        comodel_name='jewelry.client.purchase',
        inverse_name='partner_id',
        string='Client Purchases',
    )
    client_purchase_count = fields.Integer(
        string='Purchase Count',
        compute='_compute_client_purchase_count',
    )

    def _compute_client_purchase_count(self):
        """Compute purchase count using read_group for better performance."""
        purchase_data = self.env['jewelry.client.purchase'].read_group(
            domain=[('partner_id', 'in', self.ids)],
            fields=['partner_id'],
            groupby=['partner_id'],
        )
        mapped_data = {x['partner_id'][0]: x['partner_id_count'] for x in purchase_data}
        for partner in self:
            partner.client_purchase_count = mapped_data.get(partner.id, 0)

    def action_view_client_purchases(self):
        """Open list of client purchases for this partner."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Compras a Particular',
            'res_model': 'jewelry.client.purchase',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {
                'default_partner_id': self.id,
                'search_default_partner_id': self.id,
            },
        }

    def action_create_client_purchase(self):
        """Create a new client purchase for this partner."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Nueva Compra a Particular',
            'res_model': 'jewelry.client.purchase',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.id,
            },
        }
