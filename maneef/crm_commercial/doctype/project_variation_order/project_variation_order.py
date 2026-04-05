import frappe
from frappe.model.document import Document
from frappe.utils import add_days
from frappe import _

class ProjectVariationOrder(Document):
    def validate(self):
        # Calculate new total budget
        if not self.original_budget:
            self.original_budget = frappe.db.get_value("Project", self.project, "custom_contracted_fee") or 0.0
            
        self.new_total_budget = float(self.original_budget) + float(self.variation_amount or 0.0)

        # Calculate new end date
        if not self.original_end_date:
            self.original_end_date = frappe.db.get_value("Project", self.project, "expected_end_date")
            
        if self.original_end_date and self.requested_days_extension:
            self.new_end_date = add_days(self.original_end_date, self.requested_days_extension)
        else:
            self.new_end_date = self.original_end_date

        self.validate_thresholds()

    def validate_thresholds(self):
        # If variation > 10% of original budget, it needs Managing Partner
        if self.original_budget and self.original_budget > 0:
            variance_pct = abs(self.variation_amount or 0.0) / self.original_budget
            if variance_pct > 0.10:
                user_roles = frappe.get_roles(frappe.session.user)
                if "Managing Partner" not in user_roles and "System Manager" not in user_roles:
                    frappe.throw(_("Variations exceeding 10% of the original budget ({0}) require Managing Partner approval.").format(frappe.format_value(self.original_budget * 0.10, {"fieldtype": "Currency"})))

    def on_submit(self):
        self.apply_variation_to_project()

    def on_cancel(self):
        self.revert_variation_from_project()

    def apply_variation_to_project(self):
        if not self.project: return
        
        project = frappe.get_doc("Project", self.project)
        project.custom_contracted_fee = self.new_total_budget
        if self.new_end_date:
            project.expected_end_date = self.new_end_date
            
        project.save(ignore_permissions=True)
        frappe.msgprint(_("Project '{0}' updated. New Budget: {1}").format(self.project, self.new_total_budget), indicator="green", alert=True)

    def revert_variation_from_project(self):
        if not self.project: return
        
        project = frappe.get_doc("Project", self.project)
        # Safely subtract the variation amount
        current_fee = float(project.custom_contracted_fee or 0.0)
        project.custom_contracted_fee = current_fee - float(self.variation_amount or 0.0)
        
        # We cannot magically guess the previous end date if multiple variations exist,
        # but we can revert the days we added for exactly this variation.
        if project.expected_end_date and self.requested_days_extension:
            project.expected_end_date = add_days(project.expected_end_date, -(self.requested_days_extension))
            
        project.save(ignore_permissions=True)
        frappe.msgprint(_("Variation Reverted for '{0}'.").format(self.project), indicator="orange", alert=True)
