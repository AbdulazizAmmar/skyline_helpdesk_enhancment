{
    "name": "Skyline Helpdesk Enhancement",
    "version": "18.0.1.0.0",
    "summary": "Helpdesk timesheet automation, notifications, and reporting enhancements",
    "category": "Services/Helpdesk",
    "author": "Skyline",
    "license": "LGPL-3",
    "depends": ["helpdesk", "hr_timesheet", "project", "mail"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/helpdesk_views.xml",
        "reports/helpdesk_report_views.xml",
    ],
    "installable": True,
    "application": False,
}
