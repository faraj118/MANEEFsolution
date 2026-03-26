import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError
from maneef.financial_control.sales_invoice_hooks import before_submit

class TestSalesInvoiceHooks(FrappeTestCase):
    def test_revenue_lock_blocks_invoice_without_qc(self):
        project = frappe.get_doc({"doctype": "Project", "name": "Test Project"})
        project.insert()
        sales_invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "project": project.name,
            "custom_design_stage": "SD"
        })
        sales_invoice.insert()
        # No Issued+QC-approved Deliverable exists
        with self.assertRaises(ValidationError):
            before_submit(sales_invoice)
