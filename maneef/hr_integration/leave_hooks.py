"""
Maneef HR Integration — Leave Application hooks.

When a Leave Application is approved for an employee who is assigned to an
active project task, flag the Project Manager so they can re-plan deliverables.
"""

import frappe
from frappe import _


def on_update(doc, method=None):
    if doc.status != "Approved":
        return
    _notify_pm_of_leave(doc)


def _notify_pm_of_leave(leave_app):
    employee = leave_app.employee
    from_date = leave_app.from_date
    to_date = leave_app.to_date

    user_id = frappe.db.get_value("Employee", employee, "user_id")
    if not user_id:
        return

    open_tasks = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": "Task",
            "allocated_to": user_id,
            "status": "Open",
        },
        fields=["reference_name"],
    )
    if not open_tasks:
        return

    task_names = [t.reference_name for t in open_tasks]
    projects = frappe.db.sql(
        """
        SELECT DISTINCT project, custom_project_manager
        FROM `tabTask`
        WHERE name IN ({placeholders})
          AND project IS NOT NULL
          AND expected_end_date BETWEEN %s AND %s
        """.format(placeholders=", ".join(["%s"] * len(task_names))),
        task_names + [from_date, to_date],
        as_dict=True,
    )

    emp_name = frappe.db.get_value("Employee", employee, "employee_name")
    for proj in projects:
        pm = proj.get("custom_project_manager")
        if not pm:
            continue
        frappe.sendmail(
            recipients=[pm],
            subject=_("Leave Alert: {0} on leave during active task window").format(emp_name),
            message=_(
                "Employee <b>{0}</b> has an approved leave from {1} to {2}. "
                "They have open tasks on Project <b>{3}</b> that fall within this window. "
                "Please review and re-plan if necessary."
            ).format(emp_name, from_date, to_date, proj.project),
        )
