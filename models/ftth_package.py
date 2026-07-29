from odoo import fields, models


class FtthPackage(models.Model):
    _name = "ftth.package"
    _description = "FTTH Package Configuration"
    _order = "name"

    name = fields.Char(string="Package Name", required=True)
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Linked Service Product",
        domain="[('type', '=', 'service')]",
        help="Service product associated with this FTTH package.",
    )
    active = fields.Boolean(default=True)
    notes = fields.Text(string="Notes")
