import frappe
import json
import os

def create_default_roles():
    roles = [
        "Managing Partner", "Design Lead", "Technical Lead", "Doc Controller",
        "Site Architect", "BIM Coordinator", "Procurement Officer", "Project Coordinator",
        "Production Team", "Design Engineer"
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
        {"office_name": "Tripoli HQ", "city": "Tripoli", "office_type": "Strategic & Commercial"},
        {"office_name": "Cairo Production", "city": "Cairo", "office_type": "Technical & Production"}
    ]
    for office in offices:
        if not frappe.db.exists("AEC Production Office", office["office_name"]):
            try:
                frappe.get_doc({
                    "doctype": "AEC Production Office",
                    "office_name": office["office_name"],
                    "city": office["city"],
                    "office_type": office["office_type"]
                }).insert(ignore_permissions=True)
                frappe.logger().info(f"Created AEC Production Office: {office['office_name']}")
            except Exception as e:
                frappe.log_error(title="AEC Office Creation Failed", message=f"Office {office['office_name']}: {str(e)}")

def create_project_type_master():
    project_types = [
        "Innovation Projects", "Landscape Projects", "Small Construction",
        "Medium Construction", "Large Construction", "Complex Construction"
    ]
    try:
        if frappe.db.exists("DocType", "Project Type"):
            for pt in project_types:
                if not frappe.db.exists("Project Type", {"project_type": pt}):
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
            # Count of Project Deliverables awaiting any approval action
            "name": "Global Pending Approvals",
            "label": "Total Pending Approvals",
            "document_type": "Project Deliverable",
            "function": "Count",
            "filters_config": '[["Project Deliverable","docstatus","=","0"]]',
            "is_public": 1,
            "color": "Orange"
        },
        {
            # Count of open Projects where burn percentage exceeds 80%
            "name": "Average Project Burn Rate",
            "label": "High Burn Rate Projects",
            "document_type": "Project",
            "function": "Count",
            "filters_config": '[["Project","custom_burn_percentage",">=","80"],["Project","status","=","Open"]]',
            "is_public": 1,
            "color": "Red"
        }
    ]
    for card in cards:
        try:
            if not frappe.db.exists("Number Card", card["name"]):
                frappe.get_doc({"doctype": "Number Card", **card}).insert(ignore_permissions=True)
                frappe.logger().info(f"Created Number Card: {card['name']}")
                print(f"  ✅ Created Number Card: {card['name']}")
            else:
                print(f"  ⏭  Number Card already exists: {card['name']}")
        except Exception as e:
            error_msg = f"Card {card['name']}: {str(e)}"
            frappe.log_error(title="Number Card Setup Failed", message=error_msg)
            print(f"  ❌ Failed to create Number Card '{card['name']}': {str(e)}")

def setup_all_companies_coa(doc=None, method=None):
    """Automatically ensures any existing company has the Maneef AEC COA injected."""
    # Only inject COA if the company has no existing GL Entries
    if doc and frappe.db.count("GL Entry", {"company": doc.name}) > 0:
        frappe.msgprint(
            frappe._(
                "Maneef COA injection skipped for {0}: "
                "existing transactions found."
            ).format(doc.name),
            alert=True
        )
        return

    from maneef.financial_control.chart_of_accounts.coa_builder import setup_maneef_coa
    
    # If doc is provided (hook), only process that company. Otherwise (migration), process all.
    companies = [doc] if doc else frappe.get_all("Company", fields=["name"])
    
    for company in companies:
        try:
            # Re-check for GL entries in migration case (doc is None)
            if not doc and frappe.db.count("GL Entry", {"company": company.name}) > 0:
                continue
                
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
    frappe.db.commit()

def before_uninstall():
    # Remove Custom Fields added to ERPNext DocTypes
    custom_fields = frappe.get_list(
        "Custom Field",
        filters={"dt": ["not in", frappe.get_list(
            "DocType",
            filters={"module": "Maneef"},
            pluck="name"
        )]},
        pluck="name"
    )
    # Read the actual custom field names from fixtures/custom_field.json
    # and delete only those — do not delete custom fields from other apps
    import json, os
    fixtures_path = frappe.get_app_path("maneef", "fixtures", "custom_field.json")
    if os.path.exists(fixtures_path):
        with open(fixtures_path) as f:
            maneef_custom_fields = json.load(f)
        for cf in maneef_custom_fields:
            if frappe.db.exists("Custom Field", cf.get("name")):
                frappe.delete_doc("Custom Field", cf.get("name"), 
                                  ignore_missing=True, force=True)

    # Remove Property Setters
    ps_path = frappe.get_app_path("maneef", "fixtures", "property_setter.json")
    if os.path.exists(ps_path):
        with open(ps_path) as f:
            maneef_ps = json.load(f)
        for ps in maneef_ps:
            if frappe.db.exists("Property Setter", ps.get("name")):
                frappe.delete_doc("Property Setter", ps.get("name"),
                                  ignore_missing=True, force=True)

    frappe.db.commit()
    frappe.msgprint("Maneef: Custom Fields and Property Setters removed.", 
                    alert=True)
