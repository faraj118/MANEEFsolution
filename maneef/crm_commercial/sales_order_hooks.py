import frappe

from frappe import _

def before_submit(doc, method=None):
    if not doc.custom_charter_approved:
        frappe.throw(_("Project Charter must be approved before submitting Sales Order."))


def on_submit(doc, method=None):
    if not frappe.db.exists("Project", {"sales_order": doc.name}):
        # Fetch data from Project Charter if linked
        charter_data = {}
        if doc.custom_project_charter:
            charter_data = frappe.db.get_value("Project Charter", doc.custom_project_charter, 
                ["project_manager", "start_date", "end_date", "total_budget"], as_dict=1) or {}

        project = frappe.new_doc("Project")
        project.project_name = doc.customer + " - " + doc.name
        project.sales_order = doc.name
        project.custom_contract_status = "Active"
        project.status = "Open"
        
        # Pull professional metadata from Charter
        if charter_data.get("project_manager"):
            project.custom_project_manager = charter_data["project_manager"]
        if charter_data.get("start_date"):
            project.expected_start_date = charter_data["start_date"]
        if charter_data.get("end_date"):
            project.expected_end_date = charter_data["end_date"]
        if charter_data.get("total_budget"):
            project.custom_contracted_fee = charter_data["total_budget"]

        project.insert(ignore_permissions=True)
        frappe.db.set_value("Sales Order", doc.name, "project", project.name)
        frappe.logger().info(f"Auto-created Project {project.name} for Sales Order {doc.name}")
