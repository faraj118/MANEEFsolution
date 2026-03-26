import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from maneef.crm_commercial.opportunity_hooks import validate, on_update

class TestOpportunityHooks(FrappeTestCase):
    def test_validate_runs_without_error(self):
        doc = frappe.get_doc({"doctype": "Opportunity"})
        try:
            validate(doc)
        except Exception as e:
            self.fail(f"validate raised unexpected error: {e}")

    def test_on_update_runs_without_error(self):
        doc = frappe.get_doc({"doctype": "Opportunity"})
        try:
            on_update(doc)
        except Exception as e:
            self.fail(f"on_update raised unexpected error: {e}")
