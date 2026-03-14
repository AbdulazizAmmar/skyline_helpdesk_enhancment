from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    stage_last_changed_at = fields.Datetime(
        string="Stage Last Changed At",
        default=fields.Datetime.now,
        tracking=True,
        copy=False,
    )
    escalation_last_notified_at = fields.Datetime(
        string="Escalation Last Notified At",
        copy=False,
    )

    def _can_current_user_start_ticket_timesheet(self):
        """Allow timesheet start only for Supervisor/Leader/Manager groups."""
        user = self.env.user
        allowed_group_xml_ids = (
            "skyline_helpdesk_enhancment.group_helpdesk_team_supervisor",
            "skyline_helpdesk_enhancment.group_helpdesk_team_leader",
            "skyline_helpdesk_enhancment.group_helpdesk_team_manager",
        )
        return any(user.has_group(xml_id) for xml_id in allowed_group_xml_ids)

    def _ensure_timesheet_start_access(self):
        if not self._can_current_user_start_ticket_timesheet():
            raise AccessError(
                _(
                    "You are not allowed to start a new timesheet. "
                    "Only Helpdesk Team Supervisor, Team Leader, or Team Manager can do this."
                )
            )

    def _is_external_ticket_creation(self, vals):
        """Best-effort external source detection via context/values hints."""
        ctx = self.env.context
        external_context_keys = {
            "from_website",
            "website_form_submit",
            "from_mail_gateway",
            "mail_create_nolog",
            "helpdesk_from_alias",
            "from_helpdesk_alias",
            "import_file",
            "from_api",
        }
        if any(ctx.get(key) for key in external_context_keys):
            return True

        # In import mode, avoid automatic timer start.
        if ctx.get("import_file") or ctx.get("install_mode"):
            return True

        # Ticket created from incoming email usually carries email metadata.
        if vals.get("email_from") and (ctx.get("mail_create_nolog") or ctx.get("from_mail_gateway")):
            return True

        return False

    def _get_ticket_analytic_account(self):
        self.ensure_one()
        if self.project_id and self.project_id.analytic_account_id:
            return self.project_id.analytic_account_id
        return False

    def _get_active_timesheet_for_user(self, user):
        self.ensure_one()
        if not user:
            return self.env["account.analytic.line"]
        return self.env["account.analytic.line"].search(
            [
                ("helpdesk_ticket_id", "=", self.id),
                ("user_id", "=", user.id),
            ],
            order="id desc",
            limit=1,
        )

    def _create_initial_ticket_timesheet(self):
        self.ensure_one()
        if not self.user_id:
            return False

        analytic_account = self._get_ticket_analytic_account()
        if not analytic_account:
            return False

        active_line = self._get_active_timesheet_for_user(self.user_id)
        if active_line:
            return active_line

        values = {
            "name": _("Auto started from ticket: %s") % (self.display_name,),
            "helpdesk_ticket_id": self.id,
            "user_id": self.user_id.id,
            "employee_id": self.user_id.employee_id.id if self.user_id.employee_id else False,
            "account_id": analytic_account.id,
            "project_id": self.project_id.id if self.project_id else False,
            "date": fields.Date.context_today(self),
            "unit_amount": 0.0,
        }
        return self.env["account.analytic.line"].create(values)

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)

        for ticket, vals in zip(tickets, vals_list):
            if ticket._is_external_ticket_creation(vals):
                continue
            # Ticket creation itself should still succeed even when actor is not allowed.
            if not ticket._can_current_user_start_ticket_timesheet():
                continue
            ticket._create_initial_ticket_timesheet()

        return tickets

    def write(self, vals):
        stage_before = {ticket.id: ticket.stage_id.id for ticket in self}
        result = super().write(vals)

        if "stage_id" in vals:
            self._update_stage_tracking(stage_before)
            self._notify_new_to_in_progress(stage_before)

        return result

    def _update_stage_tracking(self, stage_before):
        now = fields.Datetime.now()
        for ticket in self:
            if stage_before.get(ticket.id) != ticket.stage_id.id:
                ticket.sudo().write(
                    {
                        "stage_last_changed_at": now,
                        "escalation_last_notified_at": False,
                    }
                )

    def _notify_new_to_in_progress(self, stage_before):
        new_stage = self._resolve_stage_ref(
            "helpdesk.helpdesk_stage_new", fallback_name="new"
        )
        progress_stage = self._resolve_stage_ref(
            "helpdesk.helpdesk_stage_in_progress", fallback_name="in progress"
        )

        for ticket in self:
            old_stage_id = stage_before.get(ticket.id)
            if not old_stage_id:
                continue

            old_stage = self.env["helpdesk.stage"].browse(old_stage_id)
            if self._is_stage_match(old_stage, new_stage, "new") and self._is_stage_match(
                ticket.stage_id, progress_stage, "in progress"
            ):
                self._notify_groups_by_activity(
                    ticket,
                    (
                        "skyline_helpdesk_enhancment.group_helpdesk_team_supervisor",
                        "skyline_helpdesk_enhancment.group_helpdesk_team_leader",
                    ),
                    _("Ticket moved to In Progress"),
                    _(
                        "Ticket %(ticket)s changed stage from New to In Progress."
                    )
                    % {"ticket": ticket.display_name},
                )

    @api.model
    def _resolve_stage_ref(self, xml_id, fallback_name=None):
        stage = self.env.ref(xml_id, raise_if_not_found=False)
        if stage:
            return stage
        if fallback_name:
            return self.env["helpdesk.stage"].search(
                [("name", "ilike", fallback_name)],
                limit=1,
            )
        return self.env["helpdesk.stage"]

    @api.model
    def _is_stage_match(self, stage, ref_stage, fallback_name):
        if not stage:
            return False
        if ref_stage and stage.id == ref_stage.id:
            return True
        return fallback_name.lower() in (stage.name or "").lower()

    @api.model
    def _notify_groups_by_activity(self, ticket, group_xml_ids, summary, note):
        activity_type = self.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
        if not activity_type:
            return

        model_id = self.env["ir.model"]._get_id("helpdesk.ticket")
        users = self.env["res.users"]
        for group_xml_id in group_xml_ids:
            group = self.env.ref(group_xml_id, raise_if_not_found=False)
            if group:
                users |= group.users

        users = users.filtered(lambda u: u.active)
        for user in users:
            self.env["mail.activity"].sudo().create(
                {
                    "activity_type_id": activity_type.id,
                    "summary": summary,
                    "note": note,
                    "res_model_id": model_id,
                    "res_id": ticket.id,
                    "user_id": user.id,
                }
            )

    def action_timer_start(self):
        self._ensure_timesheet_start_access()
        return super().action_timer_start()

    @api.model
    def _cron_escalate_stale_high_priority_tickets(self):
        now = fields.Datetime.now()
        one_hour_ago = now - timedelta(seconds=3600)

        tickets = self.search(
            [
                ("priority", "in", ["3", "4"]),
                ("stage_last_changed_at", "<=", one_hour_ago),
                "|",
                ("escalation_last_notified_at", "=", False),
                ("escalation_last_notified_at", "<=", one_hour_ago),
            ]
        )

        manager_group_xml_id = "skyline_helpdesk_enhancment.group_helpdesk_team_manager"
        for ticket in tickets:
            self._notify_groups_by_activity(
                ticket,
                (manager_group_xml_id,),
                _("High priority ticket needs attention"),
                _(
                    "Ticket %(ticket)s has priority %(priority)s and its stage "
                    "has not changed for at least one hour."
                )
                % {"ticket": ticket.display_name, "priority": ticket.priority},
            )
            ticket.sudo().write({"escalation_last_notified_at": now})


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    helpdesk_ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        string="Helpdesk Ticket",
        index=True,
        ondelete="set null",
    )
    helpdesk_team_id = fields.Many2one(
        comodel_name="helpdesk.team",
        string="Helpdesk Team",
        related="helpdesk_ticket_id.team_id",
        store=True,
        readonly=True,
    )
    helpdesk_stage_id = fields.Many2one(
        comodel_name="helpdesk.stage",
        string="Ticket Stage",
        related="helpdesk_ticket_id.stage_id",
        store=True,
        readonly=True,
    )
