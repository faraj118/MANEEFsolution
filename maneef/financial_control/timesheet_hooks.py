import frappe
from frappe import _

def before_submit(doc, method=None):
    settings = frappe.get_single("Maneef Settings")
    allocation_account = settings.salary_allocation_account
    default_activity_type = settings.default_activity_type or "Production / BIM"

    for row in doc.time_logs:
        if not row.project:
            continue

        if not row.activity_type:
            row.activity_type = default_activity_type

        if allocation_account and hasattr(row, "custom_allocation_account"):
            row.custom_allocation_account = allocation_account

    frappe.msgprint(_("AEC Financial Mapping Applied: Costs allocated to Project Cost Centers."))

def on_submit(doc, method=None):
    """
    Update project burn rates on timesheet submission.
    """
    for row in doc.get("time_logs", []):
        if row.project:
            _update_project_burn(row.project)

def _update_project_burn(project_name):
    if not project_name:
        return
        
    if not frappe.db.exists("Project", project_name):
        frappe.log_error(
            message="Linked to non-existent Project {0}".format(project_name),
            title="Maneef Timesheet Hook Warning"
        )
        return
        
    total_cost = frappe.db.sql("""
        SELECT SUM(costing_amount) FROM `tabTimesheet Detail` d
        JOIN `tabTimesheet` t ON d.parent = t.name
        WHERE d.project = %s AND t.docstatus = 1
    """, (project_name,))[0][0] or 0
    
    contracted_fee = frappe.db.get_value("Project", project_name, "custom_contracted_fee") or 0
    if not contracted_fee:
        frappe.log_error(f"Project '{project_name}' has 0 or null contracted fee, burn rate cannot be calculated.", "Burn Rate Error")
        return
        
    burn_pct = (total_cost / contracted_fee) * 100
    frappe.db.set_value("Project", project_name, {
        "custom_actual_cost_to_date": total_cost,
        "custom_burn_percentage": burn_pct
    })
    
    settings = frappe.get_single("Maneef Settings")
    threshold = settings.budget_alert_threshold or 80
    if burn_pct >= threshold:
        _send_burn_alert(project_name, burn_pct, threshold)

def _send_burn_alert(project_name, burn_pct, threshold=80):
    last_sent = frappe.db.get_value("Project", project_name, "custom_burn_alert_sent_at")
    if last_sent and frappe.utils.time_diff_in_hours(frappe.utils.now(), last_sent) < 24:
        return

    pm = frappe.db.get_value("Project", project_name, "custom_project_manager")
    mps = frappe.get_all("Has Role", filters={"role": "Managing Partner"}, pluck="parent")
    recipients = [pm] if pm else []
    recipients += mps
    label = "CRITICAL (OVER BUDGET)" if burn_pct >= 100 else f"WARNING ({threshold}%+ burn)"
    subject = f"{label}: Project {project_name} at {burn_pct:.1f}% burn"
    frappe.sendmail(recipients=recipients, subject=subject, message=f"Project {project_name} has reached {burn_pct:.1f}% of its contracted fee.")
    frappe.db.set_value("Project", project_name, "custom_burn_alert_sent_at", frappe.utils.now())

def daily_burn_rate_update():
    projects = frappe.get_all("Project", filters={"status": "Open"}, pluck="name")
    for project in projects:
        try:
            _update_project_burn(project)
        except Exception as e:
            frappe.log_error(str(e), "Burn Rate Update Error")

def hourly_burn_alert_check():
    threshold = frappe.get_single("Maneef Settings").budget_alert_threshold or 80
    projects = frappe.db.sql(
        "SELECT name FROM `tabProject` WHERE status='Open' AND custom_burn_percentage >= %s",
        (threshold,),
        as_dict=True,
    )
    for project in projects:
        project_name = project.name
        burn_pct = frappe.db.get_value("Project", project_name, "custom_burn_percentage")
        _send_burn_alert(project_name, burn_pct, threshold)
