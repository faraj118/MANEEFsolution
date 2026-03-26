import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from maneef.crm_commercial.sales_order_hooks import before_submit, on_submit

class TestSalesOrderHooks(FrappeTestCase):
    def test_before_submit_runs_without_error(self):
        doc = frappe.get_doc({"doctype": "Sales Order"})
        try:
            before_submit(doc)
        except Exception as e:
            self.fail(f"before_submit raised unexpected error: {e}")

    def test_on_submit_runs_without_error(self):
        doc = frappe.get_doc({"doctype": "Sales Order"})
        try:
            on_submit(doc)
        except Exception as e:
            self.fail(f"on_submit raised unexpected error: {e}")
