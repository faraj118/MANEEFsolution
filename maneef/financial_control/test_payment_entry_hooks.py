import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from maneef.financial_control.payment_entry_hooks import before_submit

class TestPaymentEntryHooks(FrappeTestCase):
    def test_before_submit_runs_without_error(self):
        doc = frappe.get_doc({"doctype": "Payment Entry"})
        try:
            before_submit(doc)
        except Exception as e:
            self.fail(f"before_submit raised unexpected error: {e}")
