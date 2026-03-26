import frappe
from frappe.model.document import Document
from frappe import _

class ProjectCharter(Document):
    def validate(self):
        self.validate_dates()
        self.fetch_customer_details()

    def on_submit(self):
        self.update_sales_order_links()
        self.create_or_update_project()

    def on_cancel(self):
        self.unlink_sales_order()
        self.deactivate_project()

    def validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw(_("Estimated End Date cannot be before Start Date"))

    def fetch_customer_details(self):
        if self.sales_order and not self.customer:
            self.customer = frappe.db.get_value("Sales Order", self.sales_order, "customer")
        elif self.opportunity and not self.customer:
            self.customer = frappe.db.get_value("Opportunity", self.opportunity, "customer")

    def update_sales_order_links(self):
        if self.sales_order:
            # Mark Sales Order as having an approved charter
            frappe.db.set_value("Sales Order", self.sales_order, {
                "custom_charter_approved": 1,
                "custom_project_charter": self.name
            })
            # Also update the Sales Order with this Charter's details if needed
            frappe.msgprint(_("Sales Order {0} linked and marked as Charter Approved").format(self.sales_order))

    def unlink_sales_order(self):
        if self.sales_order:
            frappe.db.set_value("Sales Order", self.sales_order, {
                "custom_charter_approved": 0,
                "custom_project_charter": None
            })

    def create_or_update_project(self):
        # Logic Fix: Use self.project (Link field) as the primary source of truth
        project_name = f"{self.customer} - {self.charter_name}"
        
        if self.project and frappe.db.exists("Project", self.project):
            project = frappe.get_doc("Project", self.project)
            # Update existing project with charter details
            project.expected_start_date = self.start_date
            project.expected_end_date = self.end_date
            project.custom_contracted_fee = self.total_budget
            project.save(ignore_permissions=True)
        else:
            # Create new project
            project = frappe.new_doc("Project")
            project.project_name = project_name
            project.status = "Open"
            
            office = self.get_production_office()
            if not office:
                frappe.throw(_("No 'Technical & Production' office found. Please create one in Maneef Office Master first."))
                
            project.custom_primary_office = office
            project.expected_start_date = self.start_date
            project.expected_end_date = self.end_date
            project.custom_contracted_fee = self.total_budget
            project.custom_project_manager = self.project_manager
            project.insert(ignore_permissions=True)
            
            # Use db_set to avoid re-triggering hooks on the Charter itself
            self.db_set("project", project.name)

        # Generate Tasks from Briefs
        self.generate_tasks_from_briefs(project.name)

    def get_production_office(self):
        # Logic to find a production office if not set
        return frappe.db.get_value("Maneef Office", {"office_type": "Technical & Production"}, "name")

    def generate_tasks_from_briefs(self, project_name):
        for brief in self.custom_task_briefs:
            if not frappe.db.exists("Task", {"project": project_name, "subject": brief.task_title}):
                task = frappe.new_doc("Task")
                task.project = project_name
                task.subject = brief.task_title
                task.description = brief.instruction
                task.expected_time = brief.estimated_hours
                task.status = "Open"
                # Custom branding / metadata
                task.insert(ignore_permissions=True)
                frappe.logger().info(f"Auto-created Task {task.name} for Project {project_name}")

    def deactivate_project(self):
        # Handle project cancellation if linked
        pass
