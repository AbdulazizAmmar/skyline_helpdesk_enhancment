from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    is_ftth_team = fields.Boolean(
        string="FTTH Configuration Enabled",
        default=False,
        help="Enable this setting to configure this team specifically for FTTH support and commercial workflows.",
    )
