import frappe
from frappe.model.document import Document
from frappe import _

class SVRIssue(Document):
    def validate(self):
        if not self.issue_description:
            frappe.throw(_("Issue description is required."))
        if not self.priority:
            self.priority = "Medium"

    def before_save(self):
        self.sync_project_fetch_fields()

    def sync_project_fetch_fields(self):
        if not self.project:
            return

        project = frappe.get_doc("Project", self.project)
        if project.customer:
            self.customer = project.customer
        if getattr(project, "territory", None):
            self.territory = project.territory
