import frappe
from frappe.model.document import Document

from frappe import _

class PaymentRiskAssessment(Document):
    def validate(self):
        if not self.risk_factor:
            frappe.throw(_("Risk Factor is required."))
