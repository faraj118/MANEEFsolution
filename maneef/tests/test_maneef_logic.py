import frappe
from frappe.tests.utils import FrappeTestCase
from maneef.design_operations.api import task_check_in, task_check_out

class TestManeefLogic(FrappeTestCase):
    def setUp(self):
        # Ensure Role exists
        if not frappe.db.exists("Role", "Production Team"):
            frappe.get_doc({"doctype": "Role", "role_name": "Production Team"}).insert(ignore_permissions=True)

        # Create a test office
        if not frappe.db.exists("Maneef Office", "Test Office"):
            frappe.get_doc({
                "doctype": "Maneef Office",
                "office_name": "Test Office",
                "city": "Test City",
                "office_type": "Technical & Production"
            }).insert()
            
        # Create a test project
        self.project = frappe.get_doc({
            "doctype": "Project",
            "project_name": "Test QA Project",
            "status": "Open",
            "custom_primary_office": "Test Office"
        }).insert()
        
        # Create a test task
        self.task = frappe.get_doc({
            "doctype": "Task",
            "subject": "Test QA Task",
            "project": self.project.name,
            "status": "Open"
        }).insert()

    def test_unauthorized_check_in(self):
        """Logic Guard 1: Ensure unassigned users cannot check in"""
        # Create a random user
        email = "test_cairo_qa@maneef.ly"
        if not frappe.db.exists("User", email):
            user = frappe.get_doc({
                "doctype": "User",
                "email": email,
                "first_name": "Cairo Tech",
                "roles": [{"role": "Production Team"}]
            }).insert(ignore_permissions=True)
        
        frappe.set_user(email)
        
        # This should THROW ValidationError because the task is not assigned to this user
        with self.assertRaises(frappe.ValidationError):
            task_check_in(self.task.name)

    def test_project_status_check_in(self):
        """Logic Guard 2: Ensure check-in is blocked for Closed projects"""
        # Assign the task to Administrator to pass assignment guard
        frappe.get_doc({
            "doctype": "ToDo",
            "reference_type": "Task",
            "reference_name": self.task.name,
            "description": "Test Assignment",
            "allocated_to": "Administrator",
            "status": "Open"
        }).insert(ignore_permissions=True)
        
        frappe.set_user("Administrator")
        
        # Close the project
        frappe.db.set_value("Project", self.project.name, "status", "Closed")
        
        with self.assertRaises(frappe.ValidationError):
            task_check_in(self.task.name)

    def test_timesheet_financial_mapping(self):
        """Logic Guard 3: Ensure Timesheet hooks apply AEC account mapping"""
        ts = frappe.get_doc({
            "doctype": "Timesheet",
            "user": "Administrator",
            "company": frappe.db.get_default("Company") or "Maneef Engineering",
            "time_logs": [{
                "project": self.project.name,
                "task": self.task.name,
                "from_time": "2026-03-25 08:00:00",
                "to_time": "2026-03-25 10:00:00",
                "hours": 2
            }]
        })
        # Simulate before_submit
        ts.run_method("before_submit")
        
        # Check if Activity Type was set to default AEC type
        self.assertEqual(ts.time_logs[0].activity_type, "Production / BIM")

    def tearDown(self):
        frappe.db.rollback()
