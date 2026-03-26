import frappe
import json
import os

def create_default_roles():
    roles = [
        "Managing Partner", "Design Lead", "Technical Lead", "Doc Controller",
        "Site Architect", "BIM Coordinator", "Procurement Officer", "Project Coordinator",
        "Production Team"
    ]
    for role_name in roles:
        try:
            if not frappe.db.exists("Role", role_name):
                frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)
                frappe.logger().info(f"Created role: {role_name}")
        except Exception as e:
            frappe.log_error(title="Role Creation Failed", message=f"Error creating role {role_name}: {str(e)}")

def create_default_offices():
    offices = [
        {"office_name": "Maneef HQ - Tripoli", "city": "Tripoli", "country": "Libya", "office_type": "Strategic & Commercial"},
        {"office_name": "Maneef Production - Cairo", "city": "Cairo", "country": "Egypt", "office_type": "Technical & Production"}
    ]
    for office in offices:
        try:
            if not frappe.db.exists("Maneef Office", office["office_name"]):
                frappe.get_doc({"doctype": "Maneef Office", **office}).insert(ignore_permissions=True)
                frappe.logger().info(f"Created office: {office['office_name']}")
        except Exception as e:
            frappe.log_error(title="Office Creation Failed", message=f"Error creating office {office['office_name']}: {str(e)}")

def create_project_type_master():
    project_types = [
        "Innovation Projects", "Landscape Projects", "Small Construction",
        "Medium Construction", "Large Construction", "Complex Construction"
    ]
    try:
        if frappe.db.exists("DocType", "Project Type"):
            for pt in project_types:
                if not frappe.db.exists("Project Type", pt):
                    frappe.get_doc({"doctype": "Project Type", "project_type": pt}).insert(ignore_permissions=True)
                    frappe.logger().info(f"Created Project Type: {pt}")
        else:
            frappe.logger().warning("Project Type DocType does not exist.")
    except Exception as e:
        frappe.log_error(title="Project Type Setup Failed", message=f"Error in create_project_type_master: {str(e)}")

def set_naming_series():
    series_map = {
        "Project Charter": "PC-.YYYY.-.####",
        "Transmittal": "TR-.YYYY.-.####",
        "Site Visit Report": "SVR-.YYYY.-.####"
    }
    for doctype, series in series_map.items():
        try:
            if not frappe.db.exists("Property Setter", {"doc_type": doctype, "property": "options", "field_name": "naming_series"}):
                frappe.make_property_setter({
                    "doctype": doctype,
                    "doctype_or_field": "DocField",
                    "fieldname": "naming_series",
                    "property": "options",
                    "value": series,
                    "property_type": "Text"
                })
                frappe.logger().info(f"Set naming series for {doctype}")
        except Exception as e:
            frappe.log_error(title="Naming Series Setup Failed", message=f"Error setting naming series for {doctype}: {str(e)}")

# Workflows are now handled via standard Frappe Fixtures (JSON)
# in maneef/fixtures/ directory. No programmatic insertion needed here.

def create_number_cards():
    cards = [
        {
            "name": "Deliverables Pending My Approval",
            "label": "Deliverables Pending My Approval",
            "document_type": "Project Deliverable",
            "function": "Count",
            "filters_config": '[["Project Deliverable","workflow_state","=","GM Approval Pending"]]',
            "is_public": 1,
            "color": "Blue"
        },
        {
            "name": "Projects Exceeding Burn %",
            "label": "Projects Exceeding Burn %",
            "document_type": "Project",
            "function": "Count",
            "filters_config": '[["Project","custom_burn_percentage",">","80"]]',
            "is_public": 1,
            "color": "Red"
        },
        {
            "name": "Unapproved Charters",
            "label": "Unapproved Charters",
            "document_type": "Project Charter",
            "function": "Count",
            "filters_config": '[["Project Charter","docstatus","=","0"]]',
            "is_public": 1,
            "color": "Orange"
        }
    ]
    for card in cards:
        try:
            if not frappe.db.exists("Number Card", card["name"]):
                frappe.get_doc({"doctype": "Number Card", **card}).insert(ignore_permissions=True)
                frappe.logger().info(f"Created Number Card: {card['name']}")
        except Exception as e:
            frappe.log_error(title="Number Card Setup Failed", message=f"Card {card['name']}: {str(e)}")

def setup_all_companies_coa():
    """Automatically ensures any existing company has the Maneef AEC COA injected."""
    from maneef.financial_control.chart_of_accounts.coa_builder import setup_maneef_coa
    companies = frappe.get_all("Company", fields=["name"])
    for company in companies:
        try:
            setup_maneef_coa(company.name)
        except Exception as e:
            frappe.log_error(title="AEC COA Auto-Injection Failed", message=f"Company {company.name}: {str(e)}")

def run_post_migrate_setup():
    # Main entry point for AEC system initialization
    # All Custom Fields, Workflows, and Property Setters are now 
    # handled via standard Frappe Fixtures (JSON) in maneef/fixtures/
    create_default_roles()
    create_default_offices()
    create_project_type_master()
    setup_all_companies_coa()
    
    set_naming_series()
    create_number_cards()
    frappe.logger().info("Setup complete: AEC Roles, Offices, Naming, and Cards (Workflows/Fields moved to Fixtures).")
    
    set_naming_series()
    create_number_cards()
    frappe.logger().info("Setup complete: AEC Roles, Offices, Fields, Naming, Workflows, and Cards.")
