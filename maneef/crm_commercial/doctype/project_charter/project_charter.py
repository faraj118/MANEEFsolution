import frappe
from frappe.model.document import Document
from frappe import _

from maneef.utils.permission_guard import require_permission
from maneef.utils.gate_utils import validate_gate_change

class ProjectCharter(Document):
    def validate(self):
        self.validate_dates()
        self.fetch_customer_details()
        self.validate_budget_breakdown()
        self.validate_required_fields()
        self.validate_gate_status_change()
        self.calculate_risk_totals()
        self.sync_risk_assessment()
        # NEW: Ensure Risk Assessment is updated when child tables change
        self.sync_risk_assessment_to_ra()

    def sync_risk_assessment_to_ra(self):
        """Sync Charter risk child tables to the linked Risk Assessment."""
        if not self.linked_risk_assessment:
            return

        ra = frappe.get_doc("Risk Assessment", self.linked_risk_assessment)

        child_map = [
            ("payment_risk_items", "custom_payment_risk_items"),
            ("commercial_risk_items", "custom_commercial_risk_items"),
            ("duration_risk_items", "custom_duration_risk_items"),
        ]
        for ra_field, charter_field in child_map:
            charter_rows = self.get(charter_field, [])
            if charter_rows:
                ra.set(ra_field, [row.as_dict() for row in charter_rows])

        ra.calculate_risk_totals()
        ra.save(ignore_permissions=True)

    def sync_risk_assessment(self):
        """Sync risk ratings from standalone Risk Assessment back to Charter."""
        if self.linked_risk_assessment:
            ra = frappe.get_doc("Risk Assessment", self.linked_risk_assessment)

            # Pull ratings from Risk Assessment
            if ra.payment_risk_rating:
                self.custom_payment_risk_rating = ra.payment_risk_rating
            if ra.commercial_risk_rating:
                self.custom_commercial_risk_rating = ra.commercial_risk_rating
            if ra.duration_risk_rating:
                self.custom_duration_risk_rating = ra.duration_risk_rating

            # Pull scores
            if ra.total_payment_risk_score:
                self.custom_total_payment_risk_score = ra.total_payment_risk_score
            if ra.total_commercial_risk_score:
                self.custom_total_commercial_risk_score = ra.total_commercial_risk_score
            if ra.total_duration_risk_score:
                self.custom_total_duration_risk_score = ra.total_duration_risk_score

            self.risk_assessment_status = "Completed"
        elif self.custom_payment_risk_items or self.custom_commercial_risk_items or self.custom_duration_risk_items:
            self.risk_assessment_status = "In Progress"
        else:
            self.risk_assessment_status = "Not Started"

    @frappe.whitelist()
    @require_permission("Risk Assessment", "create")
    def create_risk_assessment(self):
        """Create a new Risk Assessment linked to this Charter."""
        ra = frappe.new_doc("Risk Assessment")
        ra.project_charter = self.name
        ra.project = self.project if hasattr(self, 'project') and self.project else None
        ra.customer = self.customer
        ra.assessment_date = frappe.utils.today()
        ra.assessed_by = frappe.session.user

        ra.insert(ignore_permissions=True)

        frappe.db.set_value("Project Charter", self.name, "linked_risk_assessment", ra.name)
        frappe.db.set_value("Project Charter", self.name, "risk_assessment_status", "In Progress")

        frappe.msgprint(_("Risk Assessment {0} created successfully.").format(ra.name), indicator="green", alert=True)

        return ra.name

    def validate_gate_status_change(self):
        validate_gate_change(self)

    def on_submit(self):
        self.update_sales_order_links()
        self.create_or_update_project()

    def on_cancel(self):
        self.unlink_sales_order()
        self.deactivate_project()

    def on_trash(self):
        from maneef.utils.deletion_guard import protect_deletion

        protect_deletion(self, [
            {"doctype": "Sales Order", "link_field": "custom_project_charter", "label": "Sales Orders"},
            {"doctype": "Project", "link_field": "custom_project_charter", "label": "Projects"},
            {"doctype": "Task", "link_field": "custom_source_charter", "label": "Tasks"},
            {"doctype": "Project BOQ", "link_field": "project_charter", "label": "Project BOQs"},
            {"doctype": "Project Variation Order", "link_field": "project_charter", "label": "Variation Orders"},
        ])

    def on_update_after_submit(self):
        """
        Fires when a submitted Charter is amended/updated.
        Re-syncs dates and metadata to the linked Project to keep them in lockstep.
        """
        if self.project and frappe.db.exists("Project", self.project):
            frappe.db.set_value("Project", self.project, {
                "expected_start_date": self.start_date,
                "expected_end_date": self.end_date,
                "custom_project_manager": self.project_manager,
                "custom_contracted_fee": self.total_budget
            })
            self.sync_project_status()

    def calculate_risk_totals(self):
        payment_items = self.get("custom_payment_risk_items", [])
        if payment_items:
            total = sum(item.risk_score for item in payment_items)
            self.custom_total_payment_risk_score = total
            if total <= 7:
                self.custom_payment_risk_rating = "Low"
            elif total <= 14:
                self.custom_payment_risk_rating = "Medium"
            elif total <= 21:
                self.custom_payment_risk_rating = "High"
            else:
                self.custom_payment_risk_rating = "Unacceptable"

        commercial_items = self.get("custom_commercial_risk_items", [])
        if commercial_items:
            total = sum(item.risk_score for item in commercial_items)
            self.custom_total_commercial_risk_score = total
            if total <= 10:
                self.custom_commercial_risk_rating = "Green"
            elif total <= 20:
                self.custom_commercial_risk_rating = "Amber"
            else:
                self.custom_commercial_risk_rating = "Red"

        duration_items = self.get("custom_duration_risk_items", [])
        if duration_items:
            total = sum(item.risk_score for item in duration_items)
            self.custom_total_duration_risk_score = total
            if total <= 7:
                self.custom_duration_risk_rating = "Green"
            elif total <= 14:
                self.custom_duration_risk_rating = "Amber"
            elif total <= 21:
                self.custom_duration_risk_rating = "Red"
            else:
                self.custom_duration_risk_rating = "Critical"

    def validate_dates(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            frappe.throw(_("Estimated End Date cannot be before Start Date"))

    def fetch_customer_details(self):
        if self.sales_order and not self.customer:
            self.customer = frappe.db.get_value("Sales Order", self.sales_order, "customer")
        elif self.opportunity and not self.customer:
            self.customer = frappe.db.get_value("Opportunity", self.opportunity, "customer")

    def validate_budget_breakdown(self):
        if self.budget_breakdown:
            total = sum([b.amount for b in self.budget_breakdown if b.amount])
            if not self.total_budget:
                frappe.throw(_("Total Project Budget is required when budget breakdown is provided"))
            if abs(total - self.total_budget) > 0.01:
                frappe.throw(_("Budget breakdown total ({0}) must equal Total Project Budget ({1})").format(total, self.total_budget))

    def validate_required_fields(self):
        if not self.customer:
            frappe.throw(_("Customer is required for project creation"))
        if not self.project_manager:
            frappe.throw(_("Project manager must be assigned"))
        if not self.start_date or not self.end_date:
            frappe.throw(_("Start Date and End Date are required"))

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

    @frappe.whitelist()
    @require_permission("Project", "create", ["Managing Partner", "Project Manager", "System Manager"])
    def create_or_update_project(self):
        """
        Exclusive trigger for Project creation in Maneef AEC.
        Ensures dates, PM, and budget are strictly synced from Charter to Project.
        """
        if self.docstatus != 1:
            frappe.throw("Project Charter must be submitted before creating a Project")

        existing_project = self.project and frappe.db.exists("Project", self.project)
        action = "update" if existing_project else "create"
        frappe.logger().info(
            "Project Charter action: charter=%s project=%s user=%s action=%s",
            self.name,
            self.project,
            frappe.session.user,
            action,
        )

        project_name = f"{self.customer} - {self.charter_name}"
        
        # Check if project already exists or needs to be created
        if self.project and frappe.db.exists("Project", self.project):
            project = frappe.get_doc("Project", self.project)
        else:
            project = frappe.new_doc("Project")
            project.project_name = project_name
            project.status = "Open"
            
            # Primary Production Office setup
            office = self.get_production_office()
            if not office:
                frappe.throw(_("No 'Technical & Production' office found. Please create one in AEC Production Office Master first."))
            project.custom_primary_office = office

        # Mandatory Field Synchronization (prevents re-entry/duplicates)
        project.expected_start_date = self.start_date
        project.expected_end_date = self.end_date
        project.custom_project_manager = self.project_manager
        project.custom_contracted_fee = self.total_budget
        
        # Link back to Sales Order if available (Optional as per user request)
        if self.sales_order:
            project.sales_order = self.sales_order

        if project.is_new():
            project.insert(ignore_permissions=True)
            self.db_set("project", project.name)
        else:
            project.save(ignore_permissions=True)

        # Update Sales Order with the Project link if it exists
        if self.sales_order:
            frappe.db.set_value("Sales Order", self.sales_order, "project", project.name)

        # Sync budget breakdown to financial control
        self.sync_budget_breakdown(project.name)

        # Generate Tasks from Briefs (Task-Based Production Engine)
        self.generate_tasks_from_briefs(project.name)

    def sync_financial_control(self, project_name, budget_data):
        """Create or update financial control records for budget tracking"""
        try:
            # Check if Financial Control module is available
            if frappe.db.exists("DocType", "Project Budget Control"):
                # Create or update Project Budget Control record
                budget_control = frappe.db.exists("Project Budget Control", {"project": project_name})
                if not budget_control:
                    budget_control_doc = frappe.new_doc("Project Budget Control")
                    budget_control_doc.project = project_name
                else:
                    budget_control_doc = frappe.get_doc("Project Budget Control", budget_control)
                
                # Update budget breakdown
                budget_control_doc.budget_breakdown = []
                for item in budget_data:
                    budget_control_doc.append("budget_breakdown", {
                        "category": item["category"],
                        "description": item["description"],
                        "amount": item["amount"],
                        "percentage": item["percentage"]
                    })
                
                # Set payment terms if available
                if self.payment_terms:
                    budget_control_doc.payment_terms = self.payment_terms
                
                budget_control_doc.total_budget = self.total_budget
                budget_control_doc.save(ignore_permissions=True)
                frappe.logger().info(f"Synced budget control for Project {project_name}")
        except Exception as e:
            frappe.log_error(f"Failed to sync financial control: {str(e)}")

    @frappe.whitelist()
    def get_production_office(self):
        """Lookup the primary Technical & Production office."""
        return frappe.db.get_value(
            "AEC Production Office",
            {"office_type": "Technical & Production"},
            "name"
        )

    @frappe.whitelist()
    @require_permission(
        "Task",
        "create",
        ["Design Lead", "Design Director", "Project Manager", "Managing Partner", "System Manager"],
    )
    def generate_tasks_from_briefs(self, project_name):
        """
        Task-Based Production Engine:
        Converts each Task Brief row in the Charter into a full ERPNext Task,
        mapping all BIM-specific metadata to custom fields.
        Idempotent: skips briefs whose tasks already exist.
        """
        if self.docstatus != 1:
            frappe.throw("Project Charter must be submitted before generating tasks")

        created_count = 0
        for brief in self.custom_task_briefs:
            # Idempotency check - don't duplicate if re-submitted
            if frappe.db.exists("Task", {"project": project_name, "subject": brief.task_title}):
                continue

            task = frappe.new_doc("Task")
            task.project = project_name
            task.status = "Open"

            # Core fields
            task.subject = brief.task_title
            task.description = brief.instruction
            task.expected_time = brief.estimated_hours or 0

            # Timeline
            if brief.start_date:
                task.exp_start_date = brief.start_date

            # BIM-specific metadata (custom fields on Task)
            if hasattr(task, "custom_task_type") and brief.task_type:
                task.custom_task_type = brief.task_type
            if hasattr(task, "custom_lod_requirement") and brief.lod_requirement:
                task.custom_lod_requirement = brief.lod_requirement
            if hasattr(task, "custom_bim_discipline") and brief.bim_discipline:
                task.custom_bim_discipline = brief.bim_discipline
            if hasattr(task, "custom_bim_zone") and brief.bim_zone:
                task.custom_bim_zone = brief.bim_zone

            # Traceability: link back to the source Charter
            if hasattr(task, "custom_source_charter"):
                task.custom_source_charter = self.name

            task.insert(ignore_permissions=True)
            created_count += 1
            frappe.logger().info(f"[Maneef] Auto-created Task '{task.name}' from Brief '{brief.task_title}' for Project {project_name}")

        if created_count:
            frappe.logger().info(
                "Project Charter task generation: charter=%s project=%s created_count=%s user=%s",
                self.name,
                project_name,
                created_count,
                frappe.session.user,
            )
            frappe.msgprint(
                _("Created {0} Task(s) from Charter Task Briefs.").format(created_count),
                indicator="green",
                alert=True
            )

    def deactivate_project(self):
        """
        On Charter cancellation, gracefully close the linked Project.
        Sets the Project status to 'Cancelled' and logs the reason.
        """
        if not self.project or not frappe.db.exists("Project", self.project):
            return

        # Check for activity (Timesheets, POs, Invoices)
        has_activity = False
        activity_types = []
        
        if frappe.db.count("Timesheet Detail", {"project": self.project, "docstatus": 1}) > 0:
            has_activity = True
            activity_types.append("Timesheets")
        
        if frappe.db.count("Purchase Order", {"project": self.project, "docstatus": ["!=", 2]}) > 0:
            has_activity = True
            activity_types.append("Purchase Orders")
            
        if frappe.db.count("Sales Invoice", {"project": self.project, "docstatus": ["!=", 2]}) > 0:
            has_activity = True
            activity_types.append("Sales Invoices")
            
        if has_activity:
            frappe.msgprint(
                _("Warning: Linked Project {0} has existing activity ({1}). Cancellation will proceed, but historical records remain linked.").format(
                    self.project, ", ".join(activity_types)
                ),
                indicator="orange"
            )

        try:
            frappe.db.set_value("Project", self.project, {
                "status": "Cancelled",
                "custom_contract_status": "Cancelled"
            })
            frappe.logger().info(
                f"[Maneef] Project '{self.project}' deactivated due to Charter '{self.name}' cancellation."
            )
            frappe.msgprint(
                _("Linked Project {0} has been set to Cancelled.").format(self.project),
                indicator="orange",
                alert=True
            )
        except Exception as e:
            frappe.log_error(
                title="Project Deactivation Failed",
                message=f"Could not deactivate Project {self.project}: {str(e)}"
            )

    def sync_budget_breakdown(self, project_name):
        """Sync budget breakdown to Project custom fields for financial tracking"""
        if self.budget_breakdown:
            # Store as JSON string in custom field
            budget_data = []
            for item in self.budget_breakdown:
                budget_data.append({
                    "category": item.category,
                    "description": item.description,
                    "amount": item.amount,
                    "percentage": item.percentage
                })
            frappe.db.set_value("Project", project_name, "custom_budget_breakdown", str(budget_data))
            
            # Sync to financial control module
            self.sync_financial_control(project_name, budget_data)

    @frappe.whitelist()
    def get_project_summary(self, project_name):
        """Get project summary for sidebar display"""
        frappe.has_permission("Project", "read", project_name, throw=True)
        project = frappe.db.get_value("Project", project_name, [
            "name", "status", "custom_contracted_fee", "custom_burn_percentage"
        ], as_dict=True)

        if not project:
            return {}

        # Get task statistics
        task_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed_tasks
            FROM `tabTask`
            WHERE project = %s
        """, project_name, as_dict=True)[0]

        return {
            "project_name": project.name,
            "status": project.status,
            "contracted_fee": project.custom_contracted_fee,
            "burn_percentage": project.custom_burn_percentage or 0,
            "total_tasks": task_stats.total_tasks or 0,
            "completed_tasks": task_stats.completed_tasks or 0,
            "completion_rate": (task_stats.completed_tasks / task_stats.total_tasks * 100) if task_stats.total_tasks and task_stats.total_tasks > 0 else 0
        }

    def sync_project_status(self):
        """Sync charter status with project status"""
        if self.project:
            project_status = frappe.db.get_value("Project", self.project, "status")
            if project_status == "Completed" and self.status != "Completed":
                self.db_set("status", "Completed")
            elif project_status == "Cancelled" and self.status != "Cancelled":
                self.db_set("status", "Cancelled")
