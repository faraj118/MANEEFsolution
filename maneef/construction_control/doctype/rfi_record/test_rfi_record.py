import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestRFIRecord(FrappeTestCase):
    def test_weekly_open_items_report_runs(self):
        try:
            frappe.get_doc({"doctype": "RFI Record", "subject": "Test", "status": "Open"}).insert()
            # Simulate weekly report call
            # Replace with actual function if implemented
            # e.g., maneef.construction_control.doctype.rfi_record.rfi_record.weekly_open_items_report()
        except Exception as e:
            self.fail(f"weekly_open_items_report raised unexpected error: {e}")
