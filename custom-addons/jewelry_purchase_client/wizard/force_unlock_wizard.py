from odoo import fields, models
from odoo.exceptions import UserError


class ForceUnlockWizard(models.TransientModel):
    _name = 'jewelry.force.unlock.wizard'
    _description = 'Force Unlock Wizard'

    purchase_id = fields.Many2one(
        comodel_name='jewelry.client.purchase',
        string='Purchase Order',
        required=True,
    )
    reason = fields.Text(
        string='Reason',
        help='Optional: Explain why the blocking period is being skipped',
    )

    def action_confirm(self):
        """Force unlock the purchase order, skipping the blocking period."""
        self.ensure_one()
        if self.purchase_id.state != 'blocked':
            raise UserError('Only blocked orders can be force unlocked.')

        self.purchase_id.write({
            'state': 'available',
            'force_unlocked': True,
            'force_unlock_reason': self.reason,
            'force_unlock_date': fields.Datetime.now(),
            'force_unlock_user_id': self.env.uid,
        })

        # Audit message in chatter
        body = f'<strong>Desbloqueo forzado</strong> por {self.env.user.name}'
        if self.reason:
            body += f'<br/>Razón: {self.reason}'
        self.purchase_id.message_post(body=body, message_type='notification')

        return {'type': 'ir.actions.act_window_close'}
