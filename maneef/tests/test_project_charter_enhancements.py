"""
Test suite for Project Charter enhancements
Run with: bench --site [site] run-maneef tests.test_project_charter_enhancements
"""

import frappe
import unittest
from frappe.utils import nowdate

class TestProjectCharterEnhancements(unittest.TestCase):
    """Test cases for Project Charter enhancements"""

    def setUp(self):
        """Setup test data"""
        self.test_customer = self._get_or_create_customer()
        self.test_project_manager = self._get_or_create_user()
        self.test_office = self._get_or_create_office()

    def _get_or_create_customer(self):
        """Get or create a test customer"""
        customer_name = "Test Customer PC"
        if not frappe.db.exists("Customer", customer_name):
            customer = frappe.new_doc("Customer")
            customer.customer_name = customer_name
            customer.customer_group = "Commercial"
            customer.territory = "All Territories"
            customer.insert()
            frappe.db.commit()
        return customer_name

    def _get_or_create_user(self):
        """Get or create a test user"""
        user_email = "test_project_manager@example.com"
        if not frappe.db.exists("User", user_email):
            user = frappe.new_doc("User")
            user.email = user_email
            user.first_name = "Test"
            user.last_name = "Project Manager"
            user.send_welcome_email = 0
            user.roles = [{"role": "Project Manager"}]
            user.insert()
            frappe.db.commit()
        return user_email

    def _get_or_create_office(self):
        """Get or create a test production office"""
        office_name = "Test Technical Office"
        if not frappe.db.exists("AEC Production Office", office_name):
            office = frappe.new_doc("AEC Production Office")
            office.office_name = office_name
            office.office_type = "Technical & Production"
            office.insert()
            frappe.db.commit()
        return office_name

    def test_01_budget_breakdown_validation(self):
        """Test budget breakdown validation"""
        print("\n=== Test 1: Budget Breakdown Validation ===")

        # Create a charter with matching budget breakdown
        charter = frappe.new_doc("Project Charter")
        charter.charter_name = "Test Charter Budget"
        charter.customer = self.test_customer
        charter.project_manager = self.test_project_manager
        charter.start_date = nowdate()
        charter.end_date = nowdate()
        charter.total_budget = 10000

        # Add budget breakdown items
        charter.append("budget_breakdown", {
            "category": "Labor",
            "description": "Development work",
            "amount": 6000,
            "percentage": 60.0
        })
        charter.append("budget_breakdown", {
            "category": "Materials",
            "description": "Hardware",
            "amount": 4000,
            "percentage": 40.0
        })

        # Should pass validation
        try:
            charter.validate()
            print("✓ Budget validation passed for matching totals")
        except Exception as e:
            self.fail(f"Budget validation failed: {str(e)}")

        # Test mismatch
        charter.budget_breakdown[0].amount = 7000
        with self.assertRaises(frappe.ValidationError):
            charter.validate()
        print("✓ Budget validation correctly rejected mismatch")

    def test_02_required_fields_validation(self):
        """Test required fields validation"""
        print("\n=== Test 2: Required Fields Validation ===")

        charter = frappe.new_doc("Project Charter")
        charter.charter_name = "Test Charter Required"

        # Should fail - missing customer
        with self.assertRaises(frappe.ValidationError):
            charter.validate()
        print("✓ Correctly rejected missing customer")

        charter.customer = self.test_customer
        # Should fail - missing project manager
        with self.assertRaises(frappe.ValidationError):
            charter.validate()
        print("✓ Correctly rejected missing project manager")

        charter.project_manager = self.test_project_manager
        # Should fail - missing dates
        with self.assertRaises(frappe.ValidationError):
            charter.validate()
        print("✓ Correctly rejected missing dates")

        charter.start_date = nowdate()
        charter.end_date = nowdate()
        # Should pass now
        charter.validate()
        print("✓ All required fields validated successfully")

    def test_03_project_creation(self):
        """Test project creation from charter"""
        print("\n=== Test 3: Project Creation ===")

        charter = frappe.new_doc("Project Charter")
        charter.charter_name = "Test Charter Project Creation"
        charter.customer = self.test_customer
        charter.project_manager = self.test_project_manager
        charter.start_date = nowdate()
        charter.end_date = nowdate()
        charter.total_budget = 15000

        # Add budget breakdown
        charter.append("budget_breakdown", {
            "category": "Labor",
            "description": "Design",
            "amount": 9000,
            "percentage": 60.0
        })
        charter.append("budget_breakdown", {
            "category": "Equipment",
            "description": "Computers",
            "amount": 6000,
            "percentage": 40.0
        })

        # Submit the charter
        charter.insert()
        charter.submit()
        frappe.db.commit()

        print(f"✓ Charter submitted: {charter.name}")

        # Verify project was created
        self.assertIsNotNone(charter.project, "Project link should be set")
        self.assertTrue(frappe.db.exists("Project", charter.project),
                       f"Project {charter.project} should exist")

        project = frappe.get_doc("Project", charter.project)
        self.assertEqual(project.project_name, f"{self.test_customer} - {charter.charter_name}")
        self.assertEqual(project.expected_start_date, charter.start_date)
        self.assertEqual(project.expected_end_date, charter.end_date)
        self.assertEqual(project.custom_contracted_fee, charter.total_budget)
        self.assertEqual(project.custom_project_manager, charter.project_manager)

        print(f"✓ Project created correctly: {project.name}")

        # Verify budget breakdown synced to project
        import json
        if project.custom_budget_breakdown:
            budget_data = json.loads(project.custom_budget_breakdown)
            self.assertEqual(len(budget_data), 2, "Budget breakdown should have 2 items")
            print("✓ Budget breakdown synced to Project")

        # Verify Project Budget Control created
        if frappe.db.exists("DocType", "Project Budget Control"):
            self.assertTrue(frappe.db.exists("Project Budget Control", {"project": project.name}),
                          "Project Budget Control should be created")
            print("✓ Project Budget Control created")

        # Cleanup
        charter.cancel()
        project.cancel()
        frappe.db.delete("Project Budget Control", {"project": project.name})
        frappe.db.commit()

    def test_04_sidebar_api(self):
        """Test get_project_summary API"""
        print("\n=== Test 4: Sidebar API ===")

        # Create a project with tasks
        project = frappe.new_doc("Project")
        project.project_name = "Test API Project"
        project.status = "Open"
        project.insert()
        frappe.db.commit()

        # Create some tasks
        for i in range(3):
            task = frappe.new_doc("Task")
            task.project = project.name
            task.subject = f"Task {i+1}"
            task.status = "Open" if i < 2 else "Completed"
            task.insert()
        frappe.db.commit()

        # Test the API
        charter = frappe.new_doc("Project Charter")
        charter.charter_name = "Test Charter API"
        charter.customer = self.test_customer
        charter.project_manager = self.test_project_manager
        charter.start_date = nowdate()
        charter.end_date = nowdate()
        charter.total_budget = 5000
        charter.project = project.name
        charter.insert()

        summary = charter.get_project_summary(project.name)

        self.assertIn("project_name", summary)
        self.assertIn("status", summary)
        self.assertIn("total_tasks", summary)
        self.assertIn("completed_tasks", summary)
        self.assertIn("completion_rate", summary)
        self.assertEqual(summary["total_tasks"], 3)
        self.assertEqual(summary["completed_tasks"], 1)
        self.assertAlmostEqual(summary["completion_rate"], 33.33, places=1)

        print(f"✓ get_project_summary returned correct data: {summary}")

        # Cleanup
        frappe.db.delete("Project Charter", charter.name)
        for task in frappe.get_all("Task", {"project": project.name}):
            frappe.delete_doc("Task", task.name)
        project.delete()
        frappe.db.commit()

    def test_05_cache_functionality(self):
        """Test get_production_office caching"""
        print("\n=== Test 5: Cache Functionality ===")

        charter = frappe.new_doc("Project Charter")
        charter.charter_name = "Test Charter Cache"
        charter.customer = self.test_customer
        charter.project_manager = self.test_project_manager
        charter.start_date = nowdate()
        charter.end_date = nowdate()
        charter.total_budget = 1000

        # First call should hit database
        office1 = charter.get_production_office()
        self.assertEqual(office1, self.test_office)
        print(f"✓ First call returned: {office1}")

        # Second call should use cache
        office2 = charter.get_production_office()
        self.assertEqual(office2, office1)
        print("✓ Cache working correctly")

    def test_06_financial_control_sync(self):
        """Test financial control synchronization"""
        print("\n=== Test 6: Financial Control Sync ===")

        if not frappe.db.exists("DocType", "Project Budget Control"):
            self.skipTest("Project Budget Control doctype not available")

        charter = frappe.new_doc("Project Charter")
        charter.charter_name = "Test Charter Financial Sync"
        charter.customer = self.test_customer
        charter.project_manager = self.test_project_manager
        charter.start_date = nowdate()
        charter.end_date = nowdate()
        charter.total_budget = 25000
        charter.payment_terms = "Net 30"

        # Add budget breakdown
        charter.append("budget_breakdown", {
            "category": "Labor",
            "description": "Engineering",
            "amount": 15000,
            "percentage": 60.0
        })
        charter.append("budget_breakdown", {
            "category": "Materials",
            "description": "Supplies",
            "amount": 10000,
            "percentage": 40.0
        })

        charter.insert()
        charter.submit()
        frappe.db.commit()

        # Check Project Budget Control
        budget_control = frappe.get_doc("Project Budget Control", {"project": charter.project})
        self.assertEqual(budget_control.total_budget, charter.total_budget)
        self.assertEqual(budget_control.payment_terms, charter.payment_terms)
        self.assertEqual(len(budget_control.budget_breakdown), 2)
        print(f"✓ Project Budget Control synced correctly: {budget_control.name}")

        # Cleanup
        charter.cancel()
        frappe.delete_doc("Project Budget Control", budget_control.name)
        frappe.db.commit()

    def test_07_sidebar_configuration(self):
        """Test that sidebar fields are properly configured"""
        print("\n=== Test 7: Sidebar Configuration ===")

        # Check property setters exist
        meta = frappe.get_meta("Project Charter")

        sidebar_fields = ["project", "customer", "start_date", "end_date",
                         "total_budget", "project_priority", "risk_level"]

        for fieldname in sidebar_fields:
            field = meta.get_field(fieldname)
            self.assertIsNotNone(field, f"Field {fieldname} should exist")
            # Check if property setter exists
            prop_setter = frappe.db.exists("Property Setter", {
                "doc_type": "Project Charter",
                "fieldname": fieldname,
                "property": "sidebar_include"
            })
            self.assertIsNotNone(prop_setter, f"Property setter for {fieldname} should exist")

        print(f"✓ All {len(sidebar_fields)} sidebar fields configured")

    def test_08_new_fields_exist(self):
        """Test that all new custom fields exist"""
        print("\n=== Test 8: New Custom Fields ===")

        meta = frappe.get_meta("Project Charter")
        new_fields = ["project_priority", "risk_level", "payment_terms",
                     "budget_breakdown", "quality_gates"]

        for fieldname in new_fields:
            field = meta.get_field(fieldname)
            self.assertIsNotNone(field, f"New field {fieldname} should exist")
            print(f"✓ Field {fieldname} exists with type: {field.fieldtype}")

    def test_09_doctype_creation(self):
        """Test that new doctypes were created"""
        print("\n=== Test 9: Doctype Creation ===")

        # Check Budget Breakdown Item
        self.assertTrue(frappe.db.exists("DocType", "Budget Breakdown Item"),
                       "Budget Breakdown Item doctype should exist")
        print("✓ Budget Breakdown Item doctype exists")

        # Check Project Budget Control
        self.assertTrue(frappe.db.exists("DocType", "Project Budget Control"),
                       "Project Budget Control doctype should exist")
        print("✓ Project Budget Control doctype exists")

    def test_10_hooks_configuration(self):
        """Test hooks configuration"""
        print("\n=== Test 10: Hooks Configuration ===")

        hooks = frappe.get_hooks()
        doctype_js = hooks.get("doctype_js", {})

        self.assertIn("Project Charter", doctype_js)
        self.assertEqual(doctype_js["Project Charter"],
                        ["public/js/project_charter_sidebar.js"])
        print("✓ Project Charter JavaScript properly registered in hooks")

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("PROJECT CHARTER ENHANCEMENTS - TEST SUITE")
    print("=" * 60)

    suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectCharterEnhancements)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {len(result.failures)} FAILURES, {len(result.errors)} ERRORS")
    print("=" * 60)

    return result.wasSuccessful()

if __name__ == "__main__":
    run_tests()