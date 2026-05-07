import frappe
from frappe import _
from frappe.query_builder import DocType


def execute(filters=None):
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {"fieldname": "project", "label": _("Project"), "fieldtype": "Link", "options": "Project", "width": 150},
        {"fieldname": "project_name", "label": _("Project Name"), "fieldtype": "Data", "width": 200},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "pm", "label": _("Project Manager"), "fieldtype": "Link", "options": "User", "width": 150},
        {"fieldname": "contract_status", "label": _("Contract Status"), "fieldtype": "Data", "width": 120},
        {"fieldname": "gate_status", "label": _("Gate Status"), "fieldtype": "Data", "width": 120},
        {"fieldname": "contracted_fee", "label": _("Contracted Fee"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "actual_cost", "label": _("Actual Cost (WIP)"), "fieldtype": "Currency", "width": 130},
        {"fieldname": "burn_pct", "label": _("Burn %"), "fieldtype": "Percent", "width": 100},
        {"fieldname": "stop_work", "label": _("Stop Work Active"), "fieldtype": "Check", "width": 100},
    ]


def get_data(filters):
    Project = DocType("Project")
    query = (
        frappe.qb.from_(Project)
        .select(
            Project.name.as_("project"),
            Project.project_name,
            Project.status,
            Project.custom_project_manager.as_("pm"),
            Project.custom_contract_status.as_("contract_status"),
            Project.custom_gate_status.as_("gate_status"),
            Project.custom_contracted_fee.as_("contracted_fee"),
            Project.custom_actual_cost_to_date.as_("actual_cost"),
            Project.custom_burn_percentage.as_("burn_pct"),
            Project.custom_stop_work_active.as_("stop_work"),
        )
        .orderby(Project.custom_burn_percentage, order=frappe.qb.desc)
    )

    if filters and filters.get("status"):
        query = query.where(Project.status == filters.get("status"))

    return query.run(as_dict=True)
