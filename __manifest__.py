{
    "name": "Skyline Helpdesk Enhancement",
    "version": "19.0.1.0.0",
    "summary": "FTTH Support & Commercial Enhancements for Helpdesk",
    "category": "Services/Helpdesk",
    "author": "Skyline",
    "license": "LGPL-3",
    "depends": [
        "helpdesk",
        "analytic",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ftth_package_views.xml",
        "views/res_partner_views.xml",
        "views/helpdesk_team_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
}
