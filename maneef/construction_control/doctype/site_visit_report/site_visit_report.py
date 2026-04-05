import frappe
from frappe.model.document import Document
from frappe import _

class SiteVisitReport(Document):
    def validate(self):
        if self.is_billable:
            if not self.visit_cost or self.visit_cost <= 0:
                frappe.throw(_("A billable Site Visit MUST have a recorded Visit Cost."))
            if not self.assigned_engineer:
                frappe.throw(_("An Assigned Engineer is required for billable visits."))

    def before_save(self):
        self._auto_fill_defaults()
        self._validate_site_architect_role()

    def on_submit(self):
        self._create_issues_from_svr_issues()
        self._alert_pm_on_critical()

    def on_update_after_submit(self):
        user_roles = frappe.get_roles(frappe.session.user)
        if "Site Architect" in user_roles and not any(r in user_roles for r in ["Project Manager", "Managing Partner", "System Manager"]):
            frappe.throw(_("Edits to submitted reports are blocked for Site Architects unless you are a Project Manager or above."))

    def _auto_fill_defaults(self):
        if hasattr(self, 'site_architect') and not self.site_architect:
            self.site_architect = frappe.session.user
        if not self.assigned_engineer:
            # Check if user is linked to an Employee
            emp = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if emp:
                self.assigned_engineer = emp

        if not self.visit_date:
            self.visit_date = frappe.utils.today()
        if hasattr(frappe, 'request') and hasattr(frappe.request, 'headers'):
            ua = frappe.request.headers.get('User-Agent', '')
            self.submitted_via = "Mobile Online" if "Mobile" in ua else "Desktop"

    def _validate_site_architect_role(self):
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": ["in", ["Site Architect", "Project Manager", "Managing Partner"]]}):
            frappe.throw(_("You must have Site Architect, Project Manager, or Managing Partner role to save this report."))

    def _create_issues_from_svr_issues(self):
        for row in self.get("issues_raised", []):
            subj = f"[SVR {self.name}] {row.issue_description}"
            if not frappe.db.exists("Issue", {"subject": subj, "custom_site_visit_report": self.name}):
                issue = frappe.new_doc("Issue")
                issue.subject = subj
                issue.priority = row.priority
                issue.custom_project = self.project
                issue.custom_site_visit_report = self.name
                issue.custom_contractor = row.contractor
                issue.insert(ignore_permissions=True)

    def _alert_pm_on_critical(self):
        critical_count = sum(1 for row in self.get("issues_raised", []) if row.priority in ("High", "Critical"))
        if critical_count:
            pm = frappe.db.get_value("Project", self.project, "custom_project_manager")
            if pm:
                frappe.sendmail(recipients=[pm], subject="Critical SVR Issues", message=f"{critical_count} critical/high issues raised in SVR {self.name}.")
