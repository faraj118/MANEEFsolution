import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

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
        {"fieldname": "stop_work", "label": _("Stop Work Active"), "fieldtype": "Check", "width": 100}
    ]

def get_data(filters):
    conditions = ""
    params = ()
    if filters and filters.get("status"):
        conditions = "WHERE status = %s"
        params = (filters.get("status"),)
        
    return frappe.db.sql(f"""
        SELECT
            name as project,
            project_name,
            status,
            custom_project_manager as pm,
            custom_contract_status as contract_status,
            custom_gate_status as gate_status,
            custom_contracted_fee as contracted_fee,
            custom_actual_cost_to_date as actual_cost,
            custom_burn_percentage as burn_pct,
            custom_stop_work_active as stop_work
        FROM `tabProject`
        {conditions}
        ORDER BY custom_burn_percentage DESC
    """, params, as_dict=1)
