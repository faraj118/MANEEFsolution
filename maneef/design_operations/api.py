import frappe
from frappe import _, rate_limit
from frappe.utils import now_datetime, get_datetime, today


@frappe.whitelist()
@rate_limit(limit=30, seconds=3600)
def task_check_in(task_name):
    task = frappe.get_doc("Task", task_name)
    user = frappe.session.user

    _assert_task_assigned(task_name, user)

    project_status = frappe.db.get_value("Project", task.project, "status")
    if project_status not in ["Open", "Work in Progress"]:
        frappe.throw(
            _("Project {0} is currently {1}. You cannot record production time against a non-active project.").format(
                task.project, project_status
            )
        )

    if task.custom_check_in_status == "Checked In":
        frappe.throw(_("Already checked in to this task."))

    user_doc = frappe.get_doc("User", user)
    office = user_doc.custom_maneef_office or frappe.db.get_value(
        "Project", task.project, "custom_primary_office"
    )
    if not office:
        frappe.throw(
            _("Please assign an AEC Production Office to your User profile or the Project to track production location.")
        )

    task.custom_check_in_status = "Checked In"
    task.custom_last_check_in = now_datetime()
    task.custom_current_office = office
    task.save(ignore_permissions=True)
    return True


@frappe.whitelist()
@rate_limit(limit=30, seconds=3600)
def task_check_out(task_name):
    user = frappe.session.user
    _assert_task_assigned(task_name, user)

    task = frappe.get_doc("Task", task_name)

    if task.custom_check_in_status != "Checked In":
        frappe.throw(_("Cannot check out: task is not currently checked in."))

    if not task.custom_last_check_in:
        frappe.throw(_("Check-in time is missing. Please check in again."))

    check_in_time = get_datetime(task.custom_last_check_in)
    check_out_time = now_datetime()

    diff = check_out_time - check_in_time
    hours = max(diff.total_seconds() / 3600.0, 0.01)

    create_timesheet_entry(task, check_in_time, check_out_time, hours)

    task.custom_check_in_status = "Checked Out"
    task.save(ignore_permissions=True)
    return True


def create_timesheet_entry(task, start_time, end_time, hours):
    settings = frappe.get_single("Company Settings")
    activity_type = settings.default_activity_type or "Production / BIM"

    # Reuse today's draft timesheet for this user, or create a new one
    ts_name = frappe.db.get_value(
        "Timesheet",
        {"user": frappe.session.user, "status": "Draft", "start_date": today()},
        "name",
    )
    if ts_name:
        ts_doc = frappe.get_doc("Timesheet", ts_name)
    else:
        ts_doc = frappe.new_doc("Timesheet")
        ts_doc.user = frappe.session.user
        ts_doc.status = "Draft"
        ts_doc.insert(ignore_permissions=True)

    ts_doc.append(
        "time_logs",
        {
            "activity_type": activity_type,
            "project": task.project,
            "task": task.name,
            "from_time": start_time,
            "to_time": end_time,
            "hours": hours,
            "description": _("Production work at AEC Production Office: {0}").format(
                task.custom_current_office
            ),
        },
    )
    ts_doc.save(ignore_permissions=True)
    frappe.logger().info("Created Time Log for Task %s in Timesheet %s", task.name, ts_doc.name)


def _assert_task_assigned(task_name, user):
    if "System Manager" in frappe.get_roles(user):
        return
    assigned = frappe.db.exists(
        "ToDo",
        {"reference_type": "Task", "reference_name": task_name, "allocated_to": user, "status": "Open"},
    )
    if not assigned:
        frappe.throw(_("You are not assigned to this task. Only assigned technical staff can perform this action."))
