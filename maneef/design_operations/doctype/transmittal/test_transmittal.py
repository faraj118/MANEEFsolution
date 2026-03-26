import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestTransmittal(FrappeTestCase):
    def test_transmittal_immutable_after_submit(self):
        transmittal = frappe.get_doc({"doctype": "Transmittal", "transmittal_no": "T-001", "date": "2026-03-17", "recipient": "Test Recipient"})
        transmittal.insert()
        transmittal.submit()
        with self.assertRaises(Exception):
            transmittal.recipient = "Changed Recipient"
            transmittal.save()
