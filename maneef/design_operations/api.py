import frappe
from frappe import _, rate_limit
from frappe.utils import now_datetime, get_datetime

@frappe.whitelist()
@rate_limit(limit=30, seconds=3600)
def task_check_in(task_name):
    task = frappe.get_doc("Task", task_name)
    user = frappe.session.user
    
    # Logic Guard 1: Task Assignment
    # Check if the task is assigned to the current user
    assignments = frappe.get_all("ToDo", filters={
        "reference_type": "Task",
        "reference_name": task_name,
        "allocated_to": user,
        "status": "Open"
    })
    if not assignments and "System Manager" not in frappe.get_roles():
        frappe.throw(_("You are not assigned to this task. Only assigned technical staff can check in."))

    # Logic Guard 2: Project Status
    project_status = frappe.db.get_value("Project", task.project, "status")
    if project_status not in ["Open", "Work in Progress"]:
        frappe.throw(_("Project {0} is currently {1}. You cannot record production time against a non-active project.").format(task.project, project_status))

    if task.custom_check_in_status == 'Checked In':
        frappe.throw(_("Already checked in to this task"))
    
    # Get user's base office
    user_doc = frappe.get_doc("User", user)
    office = user_doc.custom_maneef_office
    if not office:
        # Fallback to project's office
        office = frappe.db.get_value("Project", task.project, "custom_primary_office")
    
    if not office:
        frappe.throw(_("Please assign an AEC Production Office to your User profile or the Project to track production location."))

    task.custom_check_in_status = 'Checked In'
    task.custom_last_check_in = now_datetime()
    task.custom_current_office = office
    task.save(ignore_permissions=True)
    
    return True

@frappe.whitelist()
@rate_limit(limit=30, seconds=3600)
def task_check_out(task_name):
    user = frappe.session.user
    
    # Logic Guard 1: Task Assignment
    assignments = frappe.get_all("ToDo", filters={
        "reference_type": "Task",
        "reference_name": task_name,
        "allocated_to": user,
        "status": "Open"
    })
    if not assignments and "System Manager" not in frappe.get_roles():
        frappe.throw(_("You are not assigned to this task. Only assigned technical staff can check out."))

    task = frappe.get_doc("Task", task_name)
    
    if task.custom_check_in_status == 'Checked Out':
        frappe.throw(_("Already checked out of this task"))
    
    check_in_time = get_datetime(task.custom_last_check_in)
    check_out_time = now_datetime()
    
    # Calculate duration in hours
    diff = check_out_time - check_in_time
    hours = diff.total_seconds() / 3600.0
    
    if hours < 0.01:
        hours = 0.01 # Minimum tiny fraction

    # Create Timesheet
    create_timesheet_entry(task, check_in_time, check_out_time, hours)

    task.custom_check_in_status = 'Checked Out'
    task.save(ignore_permissions=True)
    
    return True

def create_timesheet_entry(task, start_time, end_time, hours):
    # Find active timesheet for user or create one
    ts = frappe.db.get_value("Timesheet", {"user": frappe.session.user, "status": "Draft"}, "name")
    
    if not ts:
        ts_doc = frappe.new_doc("Timesheet")
        ts_doc.user = frappe.session.user
        ts_doc.status = "Draft"
        ts_doc.insert(ignore_permissions=True)
        ts = ts_doc.name
    else:
        ts_doc = frappe.get_doc("Timesheet", ts)

    ts_doc.append("time_logs", {
        "activity_type": "Production / BIM",
        "project": task.project,
        "task": task.name,
        "from_time": start_time,
        "to_time": end_time,
        "hours": hours,
        "description": _("Production work at AEC Production Office: {0}").format(task.custom_current_office)
    })
    
    ts_doc.save(ignore_permissions=True)
    frappe.logger().info(f"Created Time Log for Task {task.name} in Timesheet {ts}")
