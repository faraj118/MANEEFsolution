"""
Maneef HR Integration — Employee lifecycle hooks.

Wires HRMS Employee events into the AEC project system:
- New employee → assign default AEC Production Office based on department
- Employee designation → map to Maneef role
- Employee on_submit timesheet → enrich with employee costing rate
"""

import frappe
from frappe import _


# Department → AEC Production Office mapping
DEPT_OFFICE_MAP = {
    "Design": "Tripoli HQ",
    "BIM": "Cairo Production",
    "Production": "Cairo Production",
    "Construction": "Tripoli HQ",
    "Commercial": "Tripoli HQ",
    "Finance": "Tripoli HQ",
    "Administration": "Tripoli HQ",
}

# Designation → Maneef role mapping
DESIGNATION_ROLE_MAP = {
    "Managing Partner": "Managing Partner",
    "Design Lead": "Design Lead",
    "Technical Lead": "Technical Lead",
    "Document Controller": "Doc Controller",
    "Site Architect": "Site Architect",
    "BIM Coordinator": "BIM Coordinator",
    "Procurement Officer": "Procurement Officer",
    "Project Coordinator": "Project Coordinator",
    "Design Engineer": "Design Engineer",
}


def on_update(doc, method=None):
    """Sync employee data to User profile and assign office on save."""
    _sync_user_profile(doc)
    _assign_default_office(doc)


def after_insert(doc, method=None):
    """Assign AEC role when employee is first created."""
    _assign_maneef_role(doc)


def _sync_user_profile(employee):
    """Push AEC office from Employee back to the linked User."""
    if not employee.user_id:
        return
    office = _resolve_office(employee)
    if office and frappe.db.exists("User", employee.user_id):
        frappe.db.set_value("User", employee.user_id, "custom_maneef_office", office)


def _assign_default_office(employee):
    """Set custom_maneef_office on Employee based on department."""
    if employee.get("custom_maneef_office"):
        return
    office = _resolve_office(employee)
    if office:
        frappe.db.set_value("Employee", employee.name, "custom_maneef_office", office)


def _resolve_office(employee):
    dept = employee.department or ""
    for key, office in DEPT_OFFICE_MAP.items():
        if key.lower() in dept.lower():
            if frappe.db.exists("AEC Production Office", office):
                return office
    return None


def _assign_maneef_role(employee):
    """Assign the matching Maneef role to the linked User based on designation."""
    if not employee.user_id or not employee.designation:
        return
    role = DESIGNATION_ROLE_MAP.get(employee.designation)
    if not role:
        return
    if not frappe.db.exists("Has Role", {"parent": employee.user_id, "role": role}):
        user_doc = frappe.get_doc("User", employee.user_id)
        user_doc.append("roles", {"role": role})
        user_doc.save(ignore_permissions=True)
        frappe.logger().info("Assigned role %s to user %s via Employee %s", role, employee.user_id, employee.name)
