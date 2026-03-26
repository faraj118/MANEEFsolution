import frappe
from frappe.model.document import Document

from frappe import _

class CommercialRiskReview(Document):
    def validate(self):
        if not self.risk_area:
            frappe.throw(_("Risk Area is required."))
