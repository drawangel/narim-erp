from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    jewelry_blocking_days = fields.Integer(
        string='Legal Blocking Days',
        help='Number of days items must be held before sending to smelting (police requirement)',
        config_parameter='jewelry.blocking_days',
        default=14,
    )
    jewelry_default_pawn_margin = fields.Float(
        string='Default Pawn Margin (%)',
        help='Default margin percentage for pawn recovery price',
        config_parameter='jewelry.default_pawn_margin',
        default=20.0,
    )
    jewelry_default_daily_surcharge = fields.Float(
        string='Default Daily Surcharge (%)',
        help='Default daily surcharge percentage after pawn due date',
        config_parameter='jewelry.default_daily_surcharge',
        default=0.5,
    )
