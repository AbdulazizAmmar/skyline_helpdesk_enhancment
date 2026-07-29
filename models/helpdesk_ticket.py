from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    is_ftth_team = fields.Boolean(
        related="team_id.is_ftth_team",
        string="Is FTTH Team",
        readonly=True,
        store=True,
    )

    ftth_package_id = fields.Many2one(
        comodel_name="ftth.package",
        string="Package Name",
        help="Linked FTTH subscription package",
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

    @api.onchange("partner_id")
    def _onchange_partner_id_ftth_details(self):
        if self.partner_id and self.is_ftth_team:
            self.ftth_package_id = self.partner_id.ftth_package_id
            self.ftth_username = self.partner_id.ftth_username
            self.ftth_serial_number = self.partner_id.ftth_serial_number
            self.ftth_activation_code = self.partner_id.ftth_activation_code
            self.ftth_zone_id = self.partner_id.ftth_zone_id
            self.ftth_fat = self.partner_id.ftth_fat

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            partner_id = vals.get("partner_id")
            team_id = vals.get("team_id")
            if partner_id and team_id:
                team = self.env["helpdesk.team"].browse(team_id)
                if team.is_ftth_team:
                    partner = self.env["res.partner"].browse(partner_id)
                    vals.setdefault("ftth_package_id", partner.ftth_package_id.id if partner.ftth_package_id else False)
                    vals.setdefault("ftth_username", partner.ftth_username)
                    vals.setdefault("ftth_serial_number", partner.ftth_serial_number)
                    vals.setdefault("ftth_activation_code", partner.ftth_activation_code)
                    vals.setdefault("ftth_zone_id", partner.ftth_zone_id.id if partner.ftth_zone_id else False)
                    vals.setdefault("ftth_fat", partner.ftth_fat)
        return super().create(vals_list)
