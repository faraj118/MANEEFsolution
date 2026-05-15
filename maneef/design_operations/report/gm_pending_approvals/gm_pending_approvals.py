import frappe
from frappe import _
from frappe.utils import getdate, nowdate


def execute(filters=None):
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {
            "fieldname": "name",
            "label": _("Deliverable"),
            "fieldtype": "Link",
            "options": "Project Deliverable",
            "width": 160,
        },
        {
            "fieldname": "deliverable_name",
            "label": _("Deliverable Name"),
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "fieldname": "project",
            "label": _("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": 150,
        },
        {
            "fieldname": "customer",
            "label": _("Client"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "fieldname": "deliverable_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "discipline",
            "label": _("Discipline"),
            "fieldtype": "Data",
            "width": 110,
        },
        {
            "fieldname": "revision",
            "label": _("Rev."),
            "fieldtype": "Data",
            "width": 60,
        },
        {
            "fieldname": "assigned_to",
            "label": _("Assigned To"),
            "fieldtype": "Link",
            "options": "User",
            "width": 140,
        },
        {
            "fieldname": "due_date",
            "label": _("Due Date"),
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "fieldname": "days_overdue",
            "label": _("Days Overdue"),
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "fieldname": "design_lead_approved",
            "label": _("Design Lead"),
            "fieldtype": "Check",
            "width": 100,
        },
        {
            "fieldname": "technical_lead_approved",
            "label": _("Tech Lead"),
            "fieldtype": "Check",
            "width": 90,
        },
        {
            "fieldname": "principal_approved",
            "label": _("Principal"),
            "fieldtype": "Check",
            "width": 90,
        },
    ]


def get_data(filters):
    conditions = {"workflow_state": "GM Approval Pending"}

    if filters:
        if filters.get("project"):
            conditions["project"] = filters["project"]
        if filters.get("deliverable_type"):
            conditions["deliverable_type"] = filters["deliverable_type"]

    rows = frappe.get_all(
        "Project Deliverable",
        filters=conditions,
        fields=[
            "name",
            "deliverable_name",
            "project",
            "customer",
            "deliverable_type",
            "discipline",
            "revision",
            "assigned_to",
            "due_date",
            "design_lead_approved",
            "technical_lead_approved",
            "principal_approved",
        ],
        order_by="due_date asc",
    )

    today = getdate(nowdate())
    for row in rows:
        if row.due_date:
            delta = (today - getdate(row.due_date)).days
            row["days_overdue"] = delta if delta > 0 else 0
        else:
            row["days_overdue"] = 0

    if filters and filters.get("overdue_only"):
        rows = [r for r in rows if r["days_overdue"] > 0]

    return rows
