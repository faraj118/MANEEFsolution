"""
HRMS post-install setup for Maneef.

Creates HR masters that the AEC workflow depends on:
- Department tree (Design, BIM, Construction, Commercial, Finance)
- Designations matching Maneef roles
- Default Leave Types
- Employee Grade → Costing Rate mapping
"""

import frappe


AEC_DEPARTMENTS = [
    "Design",
    "BIM",
    "Construction",
    "Commercial",
    "Finance",
    "Administration",
]

AEC_DESIGNATIONS = [
    "Managing Partner",
    "Design Lead",
    "Technical Lead",
    "Document Controller",
    "Site Architect",
    "BIM Coordinator",
    "Procurement Officer",
    "Project Coordinator",
    "Design Engineer",
    "Site Engineer",
]

AEC_LEAVE_TYPES = [
    {"leave_type_name": "Annual Leave", "max_leaves_allowed": 21, "is_carry_forward": 1},
    {"leave_type_name": "Sick Leave", "max_leaves_allowed": 14, "is_carry_forward": 0},
    {"leave_type_name": "Unpaid Leave", "max_leaves_allowed": 0, "is_carry_forward": 0},
    {"leave_type_name": "Compensatory Off", "max_leaves_allowed": 0, "is_carry_forward": 0},
]


def setup_hr_masters():
    _create_departments()
    _create_designations()
    _create_leave_types()
    frappe.db.commit()
    frappe.logger().info("Maneef HRMS masters created.")


def _create_departments():
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        companies = frappe.get_all("Company", pluck="name", limit=1)
        company = companies[0] if companies else None

    for dept in AEC_DEPARTMENTS:
        if not frappe.db.exists("Department", {"department_name": dept}):
            try:
                frappe.get_doc({
                    "doctype": "Department",
                    "department_name": dept,
                    "company": company,
                }).insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(str(e), f"AEC Department creation failed: {dept}")


def _create_designations():
    for desig in AEC_DESIGNATIONS:
        if not frappe.db.exists("Designation", desig):
            try:
                frappe.get_doc({
                    "doctype": "Designation",
                    "designation_name": desig,
                }).insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(str(e), f"AEC Designation creation failed: {desig}")


def _create_leave_types():
    for lt in AEC_LEAVE_TYPES:
        if not frappe.db.exists("Leave Type", lt["leave_type_name"]):
            try:
                frappe.get_doc({"doctype": "Leave Type", **lt}).insert(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(str(e), f"AEC Leave Type creation failed: {lt['leave_type_name']}")
