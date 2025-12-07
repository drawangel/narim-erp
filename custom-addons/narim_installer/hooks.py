import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def post_init_hook(env):
    """
    Operaciones post-instalación:
    1. Desactivar OdooBot para todos los usuarios (método estándar).
    """
    disable_odoobot(env)

def disable_odoobot(env):
    _logger.info("NarimERP: Asegurando que OdooBot esté desactivado...")
    # Solo cambiamos el estado, sin borrar datos ni actividades.
    users = env['res.users'].with_context(active_test=False).search([
        ('odoobot_state', '!=', 'disabled')
    ])
    
    if users:
        users.write({'odoobot_state': 'disabled'})
