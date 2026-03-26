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

def on_timesheet_submit(doc, method=None):
    for row in doc.get("time_logs", []):
        if row.project:
            _update_project_burn(row.project)

def _update_project_burn(project_name):
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
    if burn_pct >= 80:
        _send_burn_alert(project_name, burn_pct)

def _send_burn_alert(project_name, burn_pct):
    last_sent = frappe.db.get_value("Project", project_name, "custom_burn_alert_sent_at")
    if last_sent and frappe.utils.time_diff_in_hours(frappe.utils.now(), last_sent) < 24:
        return

    pm = frappe.db.get_value("Project", project_name, "custom_project_manager")
    mps = frappe.get_all("Has Role", filters={"role": "Managing Partner"}, pluck="parent")
    recipients = [pm] if pm else []
    recipients += mps
    subject = f"{'CRITICAL (OVER BUDGET)' if burn_pct >= 100 else 'WARNING (80%+ burn)'}: Project {project_name} at {burn_pct:.1f}% burn"
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
    projects = frappe.db.sql("""
        SELECT name FROM `tabProject` WHERE status='Open' AND custom_burn_percentage >= 80
    """)
    for (project_name,) in projects:
        burn_pct = frappe.db.get_value("Project", project_name, "custom_burn_percentage")
        _send_burn_alert(project_name, burn_pct)
