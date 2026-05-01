import frappe
from frappe import _

def before_submit(doc, method=None):
    design_stage = doc.custom_design_stage
    project = doc.project
    if design_stage and project:
        found = frappe.db.exists("Project Deliverable", {
            "project": project,
            "design_stage": design_stage,
            "qc_checklist_approved": 1,
            "status": "Issued",
            "docstatus": 1
        })
        if not found:
            frappe.log_error(f"Revenue Lock: Invoice {doc.name} blocked for project {project}, stage {design_stage}", "Revenue Lock (BRD 9.1)")
            frappe.throw(_("Revenue Lock (BRD 9.1): Technical Lead must approve the QC Checklist for this stage before invoicing."))

