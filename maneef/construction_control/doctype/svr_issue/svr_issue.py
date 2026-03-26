import frappe
from frappe.model.document import Document
from frappe import _

class SvrIssue(Document):
    def validate(self):
        if not self.issue_description:
            frappe.throw(_("Issue description is required."))
        if not self.priority:
            self.priority = "Medium"
