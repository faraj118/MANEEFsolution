import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.exceptions import ValidationError

class TestProjectDeliverable(FrappeTestCase):
    def test_ip_lock_blocks_without_signed_so(self):
        # Setup: Project without Sales Order
        project = frappe.get_doc({"doctype": "Project", "name": "Test Project"})
        project.insert()
        deliverable = frappe.get_doc({"doctype": "Project Deliverable", "project": project.name})
        with self.assertRaises(ValidationError) as ctx:
            deliverable.insert()
        self.assertIn("IP Protection Lock", str(ctx.exception))

    def test_ip_lock_passes_with_signed_so(self):
        project = frappe.get_doc({"doctype": "Project", "name": "Test Project 2"})
        project.insert()
        sales_order = frappe.get_doc({
            "doctype": "Sales Order",
            "project": project.name,
            "custom_contract_status": "Signed",
            "docstatus": 1
        })
        sales_order.insert()
        deliverable = frappe.get_doc({"doctype": "Project Deliverable", "project": project.name})
        try:
            deliverable.insert()
        except ValidationError:
            self.fail("IP Lock should not block with signed SO")

    def test_bim_lod_violation(self):
        project = frappe.get_doc({
            "doctype": "Project",
            "name": "Test Project 3",
            "custom_project_type": "Small Construction"
        })
        project.insert()
        deliverable = frappe.get_doc({
            "doctype": "Project Deliverable",
            "project": project.name,
            "bim_lod": "LOD 400"
        })
        with self.assertRaises(ValidationError) as ctx:
            deliverable.insert()
        self.assertIn("LOD 300", str(ctx.exception))
