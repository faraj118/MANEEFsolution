from __future__ import annotations

import frappe
from frappe import _


def before_submit(doc, method=None) -> None:
    design_stage: str = doc.custom_design_stage
    project: str = doc.project
    if not design_stage or not project:
        return

    # Revenue Lock (BRD 9.1): a submitted, Issued Project Deliverable for this
    # project/stage must exist with Technical Lead approval before revenue is recognised.
    found = frappe.db.exists(
        "Project Deliverable",
        {
            "project": project,
            "design_stage": design_stage,
            "technical_lead_approved": 1,
            "status": "Issued",
            "docstatus": 1,
        },
    )
    if not found:
        frappe.log_error(
            f"Revenue Lock: Invoice {doc.name} blocked — project {project}, stage {design_stage}",
            "Revenue Lock (BRD 9.1)",
        )
        frappe.throw(
            _(
                "Revenue Lock (BRD 9.1): A submitted, Issued Project Deliverable for stage '{0}' "
                "with Technical Lead approval must exist before this invoice can be submitted."
            ).format(design_stage)
        )

