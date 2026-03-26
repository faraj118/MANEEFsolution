import frappe
from frappe.model.document import Document

from frappe import _

class CharterScopePackage(Document):
    def validate(self):
        if not self.package_name:
            frappe.throw(_("Package Name is required."))
