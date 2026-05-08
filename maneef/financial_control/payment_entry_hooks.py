import frappe
from frappe import _


def before_submit(doc, method=None):
    if not doc.custom_is_payment_certificate:
        return

    project = doc.custom_project
    if not project:
        return

    settings = frappe.get_single("Maneef Settings")
    sla_days = settings.snag_resolution_sla_days or 14

    snag_list_name = frappe.db.get_value("Snag List", {"project": project, "status": "Active"}, "name")
    if not snag_list_name:
        return

    sl = frappe.get_doc("Snag List", snag_list_name)
    today = frappe.utils.getdate(frappe.utils.today())

    blocking_snags = [
        s for s in sl.get("snags", [])
        if s.priority == "Critical"
        and s.status in ("Open", "In Progress")
        and s.due_date
        and frappe.utils.date_diff(today, frappe.utils.getdate(s.due_date)) > sla_days
    ]

    if blocking_snags:
        descriptions = ", ".join(
            '"{0}" (due {1})'.format(s.description[:50], s.due_date)
            for s in blocking_snags
        )
        frappe.throw(
            _("Payment blocked: {0} Critical snag(s) are overdue by more than {1} days on Project {2}. "
              "Resolve all overdue Critical snags before releasing payment. Blocking snags: {3}").format(
                len(blocking_snags), sla_days, project, descriptions
            )
        )
