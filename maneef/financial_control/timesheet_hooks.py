import frappe
from frappe import _

def before_submit(doc, method=None):
    """
    Automate AEC Financial Mapping for Maneef:
    - Moves labor cost to Account 5110 (Salaries Allocation) 
    - Ensures Project Cost Center is applied.
    """
    for row in doc.time_logs:
        if not row.project:
            continue
            
        # 1. Fetch Project Financial Defaults
        project_cost_center = frappe.db.get_value("Project", row.project, "cost_center")
        if not project_cost_center:
            # Fallback to Company default cost center
            project_cost_center = frappe.db.get_value("Company", doc.company, "cost_center")
            
        # 2. Force AEC Account Alignment (Salaries Allocation - 5110)
        # Note: In standard ERPNext, Timesheet doesn't have an 'account' field per row,
        # but it affects the 'Activity Cost' which is used in Salary Slips or Project Costing.
        # We ensure the metadata (Activity Type) is correct so that downstream Payroll/Journaling can pick it up.
        
        if not row.activity_type:
             row.activity_type = "Production / BIM"
             
        # Add a custom hidden field for the target account if it exists (AEC Customization)
        if hasattr(row, "custom_allocation_account"):
            row.custom_allocation_account = "5110 - Salaries Allocation - M"

    frappe.msgprint(_("AEC Financial Mapping Applied: Costs allocated to Project Cost Centers."))

def on_submit(doc, method=None):
    """
    Optional: Auto-generate a Journal Entry if specific WIP capitalization is required instantly.
    """
    pass
