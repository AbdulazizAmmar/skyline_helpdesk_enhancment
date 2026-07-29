from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_ftth_customer = fields.Boolean(
        string="Is FTTH Customer",
        default=False,
        help="Check this box if the contact is an FTTH (Fiber to the Home) customer.",
        tracking=True,
    )
    ftth_package_id = fields.Many2one(
        comodel_name="ftth.package",
        string="Package Name",
        help="Linked FTTH subscription package.",
    )
    ftth_username = fields.Char(
        string="FTTH Username",
        help="Customer PPPoE / Service Username",
    )
    ftth_serial_number = fields.Char(
        string="Serial Number",
        help="ONT / Router Serial Number",
    )
    ftth_activation_code = fields.Char(
        string="Activation Code",
        help="FTTH Service Activation Code",
    )
    ftth_zone_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Zone",
        help="FTTH Geographic Zone / Analytic Account",
    )
    ftth_fat = fields.Char(
        string="FAT",
        help="Fiber Access Terminal (FAT) Identifier",
    )
