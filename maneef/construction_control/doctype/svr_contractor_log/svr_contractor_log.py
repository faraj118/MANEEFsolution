import frappe
from frappe.model.document import Document
from frappe import _

class SVRContractorLog(Document):
    def validate(self):
        if not self.contractor:
            frappe.throw(_("Contractor is required in every contractor log row."))
