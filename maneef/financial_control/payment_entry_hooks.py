from __future__ import annotations

import frappe
from frappe import _


def before_submit(doc, method=None) -> None:
    if not doc.custom_is_payment_certificate:
        return

    project: str = doc.custom_project
    if not project:
        return

    settings = frappe.get_single("Company Settings")
    sla_days: int = settings.snag_resolution_sla_days or 14

    blocking_snags = frappe.db.sql(
        """
        SELECT si.name, si.description, si.due_date
        FROM `tabSnag Item` si
        JOIN `tabSnag List` sl ON si.parent = sl.name
        WHERE sl.project = %s
          AND sl.status = 'Active'
          AND si.priority = 'Critical'
          AND si.status IN ('Open', 'In Progress')
          AND si.due_date IS NOT NULL
          AND DATEDIFF(CURDATE(), DATE(si.due_date)) > %s
        LIMIT 100
        """,
        (project, sla_days),
        as_dict=True,
    )

    if blocking_snags:
        descriptions = ", ".join(
            '"{0}" (due {1})'.format(s.description[:50], s.due_date) for s in blocking_snags
        )
        frappe.throw(
            _(
                "Payment blocked: {0} Critical snag(s) are overdue by more than {1} days on Project {2}. "
                "Resolve all overdue Critical snags before releasing payment. Blocking snags: {3}"
            ).format(len(blocking_snags), sla_days, project, descriptions)
        )
