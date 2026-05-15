from __future__ import annotations

import frappe
from frappe import _


def before_submit(doc, method=None) -> None:
    settings = frappe.get_single("Company Settings")
    allocation_account: str | None = settings.salary_allocation_account
    default_activity_type: str = settings.default_activity_type or "Production / BIM"

    for row in doc.time_logs:
        if not row.project:
            continue
        if not row.activity_type:
            row.activity_type = default_activity_type
        if allocation_account and hasattr(row, "custom_allocation_account"):
            row.custom_allocation_account = allocation_account

    if frappe.flags.in_web_form or frappe.local.get("site"):
        frappe.msgprint(_("AEC Financial Mapping Applied: Costs allocated to Project Cost Centers."))


def on_submit(doc, method=None) -> None:
    for row in doc.get("time_logs", []):
        if row.project:
            _update_project_burn(row.project)


def _update_project_burn(project_name: str) -> None:
    if not project_name:
        return

    if not frappe.db.exists("Project", project_name):
        frappe.log_error(
            message="Linked to non-existent Project {0}".format(project_name),
            title="Maneef Timesheet Hook Warning",
        )
        return

    total_cost: float = (
        frappe.db.sql(
            """
            SELECT COALESCE(SUM(td.costing_amount), 0)
            FROM `tabTimesheet Detail` td
            JOIN `tabTimesheet` t ON td.parent = t.name
            WHERE td.project = %s AND t.docstatus = 1
            """,
            (project_name,),
        )[0][0]
        or 0
    )

    contracted_fee: float = float(
        frappe.db.get_value("Project", project_name, "custom_contracted_fee") or 0
    )
    if contracted_fee <= 0:
        frappe.throw(
            _("Project '{0}' has no contracted fee set. Burn rate cannot be calculated.").format(
                project_name
            )
        )

    burn_pct: float = (total_cost / contracted_fee) * 100
    frappe.db.set_value(
        "Project",
        project_name,
        {
            "custom_actual_cost_to_date": total_cost,
            "custom_burn_percentage": burn_pct,
        },
    )

    settings = frappe.get_single("Company Settings")
    threshold: float = settings.budget_alert_threshold or 80
    if burn_pct >= threshold:
        _send_burn_alert(project_name, burn_pct, threshold)


def _send_burn_alert(project_name: str, burn_pct: float, threshold: float = 80) -> None:
    settings = frappe.get_single("Company Settings")
    cooldown_hours: float = settings.burn_alert_cooldown_hours or 24

    last_sent = frappe.db.get_value("Project", project_name, "custom_burn_alert_sent_at")
    if last_sent and frappe.utils.time_diff_in_hours(frappe.utils.now(), last_sent) < cooldown_hours:
        return

    pm: str | None = frappe.db.get_value("Project", project_name, "custom_project_manager")
    mps: list[str] = frappe.get_all(
        "Has Role", filters={"role": "Managing Partner"}, pluck="parent"
    )

    seen: set[str] = set()
    recipients: list[str] = []
    for r in ([pm] if pm else []) + mps:
        if r and r not in seen:
            seen.add(r)
            recipients.append(r)

    label = "CRITICAL (OVER BUDGET)" if burn_pct >= 100 else f"WARNING ({threshold}%+ burn)"
    subject = f"{label}: Project {project_name} at {burn_pct:.1f}% burn"
    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=f"Project {project_name} has reached {burn_pct:.1f}% of its contracted fee.",
    )
    frappe.db.set_value("Project", project_name, "custom_burn_alert_sent_at", frappe.utils.now())


def daily_burn_rate_update() -> None:
    """Bulk burn-rate sync: single JOIN query replaces the per-project N+1 pattern."""
    projects_data = frappe.db.sql(
        """
        SELECT p.name, p.custom_contracted_fee,
               COALESCE(SUM(td.costing_amount), 0) AS total_cost
        FROM `tabProject` p
        LEFT JOIN `tabTimesheet Detail` td ON td.project = p.name
        LEFT JOIN `tabTimesheet` t ON td.parent = t.name AND t.docstatus = 1
        WHERE p.status = 'Open'
        GROUP BY p.name, p.custom_contracted_fee
        """,
        as_dict=True,
    )

    settings = frappe.get_single("Company Settings")
    threshold: float = settings.budget_alert_threshold or 80

    for row in projects_data:
        contracted_fee = float(row.custom_contracted_fee or 0)
        total_cost = float(row.total_cost or 0)

        if contracted_fee <= 0:
            frappe.log_error(
                f"Project '{row.name}' has 0 or null contracted fee; burn rate skipped.",
                "Burn Rate Scheduler Error",
            )
            continue

        burn_pct: float = (total_cost / contracted_fee) * 100

        frappe.db.set_value(
            "Project",
            row.name,
            {
                "custom_actual_cost_to_date": total_cost,
                "custom_burn_percentage": burn_pct,
            },
        )

        if burn_pct >= threshold:
            frappe.enqueue(
                "maneef.financial_control.timesheet_hooks._send_burn_alert",
                project_name=row.name,
                burn_pct=burn_pct,
                threshold=threshold,
                queue="default",
            )


def hourly_burn_alert_check() -> None:
    """Re-check all at-threshold projects; dispatch alert emails asynchronously."""
    threshold: float = frappe.get_single("Company Settings").budget_alert_threshold or 80

    projects = frappe.db.sql(
        """
        SELECT name, custom_burn_percentage
        FROM `tabProject`
        WHERE status = 'Open' AND custom_burn_percentage >= %s
        """,
        (threshold,),
        as_dict=True,
    )

    for project in projects:
        frappe.enqueue(
            "maneef.financial_control.timesheet_hooks._send_burn_alert",
            project_name=project.name,
            burn_pct=project.custom_burn_percentage,
            threshold=threshold,
            queue="default",
        )
