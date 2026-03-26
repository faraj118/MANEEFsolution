import frappe
from frappe.model.document import Document
from frappe import _

class SnagItem(Document):
    def validate(self):
        if self.priority in ("High", "Critical") and self.status == "Resolved":
            if not self.resolved_by or not self.resolution_date:
                frappe.throw(_("High/Critical snags require both 'resolved_by' and 'resolution_date'."))

    def on_update(self):
        if self.status == "Resolved" and self.custom_project:
            all_resolved = not frappe.get_all("Snag Item", filters={"custom_project": self.custom_project, "status": ["not in", ["Resolved"]]})
            if all_resolved:
                pm = frappe.db.get_value("Project", self.custom_project, "custom_project_manager")
                if pm:
                    frappe.publish_realtime("snags_cleared", {"project": self.custom_project}, user=pm)
