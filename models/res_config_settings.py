from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_skyline_helpdesk_enhancment = fields.Boolean(
        string="FTTH Support & Commercial Enhancement",
        default=True,
    )
