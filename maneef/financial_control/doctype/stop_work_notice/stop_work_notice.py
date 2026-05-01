import frappe
from frappe.model.document import Document
from frappe import _
from maneef.utils.permission_guard import require_permission

class StopWorkNotice(Document):
    def before_submit(self):
        self.issued_by = frappe.session.user
        self.issued_date = frappe.utils.now()
        self.status = "Active"
        frappe.db.set_value("Project", self.project, "custom_stop_work_active", 1)

    def on_update_after_submit(self):
        if self.status != "Lifted":
            frappe.throw(_("Stop-Work Notice is immutable once issued. Only the Managing Partner can lift it via the Lift Notice action."))

    def on_cancel(self):
        frappe.throw(_("Stop-Work Notices cannot be cancelled. Use the Lift Notice action if the issue has been resolved."))

    @frappe.whitelist()
    @require_permission("Stop Work Notice", "write")
    def lift_stop_work(self):
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "Managing Partner"}):
            frappe.throw(_("Only a Managing Partner can lift a Stop-Work Notice."))
        frappe.db.set_value("Stop Work Notice", self.name, {
            "status": "Lifted",
            "lifted_by": frappe.session.user,
            "lifted_date": frappe.utils.now()
        })
        frappe.db.set_value("Project", self.project, "custom_stop_work_active", 0)
        frappe.msgprint(_("Stop-Work Notice lifted. Project deliverables are unblocked."), indicator="green")
