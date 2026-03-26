import frappe
from frappe.model.document import Document

from frappe import _

class AssumptionsLog(Document):
    def validate(self):
        if not self.assumption:
            frappe.throw(_("Assumption is required."))
