import frappe
from frappe.model.document import Document
from frappe import _

class SvrPhoto(Document):
    def validate(self):
        if self.photo_file and not self.caption:
            frappe.msgprint(_("Please add a caption describing what this photo shows."))

# ---

class SvrContractorLog(Document):
    def validate(self):
        if not self.contractor:
            frappe.throw(_("Contractor is required in every contractor log row."))

# ---

class SvrIssue(Document):
    def validate(self):
        if not self.issue_description:
            frappe.throw(_("Issue description is required."))
        if not self.priority:
            self.priority = "Medium"
