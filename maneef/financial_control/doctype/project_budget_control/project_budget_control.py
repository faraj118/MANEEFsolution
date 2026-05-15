import frappe
from frappe.model.document import Document
from frappe import _

class ProjectBudgetControl(Document):
    def validate(self):
        self.calculate_variance()
        self.calculate_burn_percentage()

    def before_save(self):
        self.set_last_synced()

    def calculate_variance(self):
        from frappe.utils import flt
        budget = flt(self.total_budget)
        actual = flt(self.actual_cost_to_date)
        if budget > 0:
            self.budget_variance = budget - actual
            self.variance_percentage = (self.budget_variance / budget) * 100

    def calculate_burn_percentage(self):
        from frappe.utils import flt
        budget = flt(self.total_budget)
        actual = flt(self.actual_cost_to_date)
        if budget > 0:
            self.burn_percentage = (actual / budget) * 100

    def set_last_synced(self):
        self.last_synced = frappe.utils.now()

    def update_from_charter(self, charter_doc):
        """Update budget control from Project Charter"""
        self.project = charter_doc.project
        self.total_budget = charter_doc.total_budget
        
        # Sync budget breakdown
        if charter_doc.budget_breakdown:
            self.budget_breakdown = []
            for item in charter_doc.budget_breakdown:
                self.append("budget_breakdown", {
                    "category": item.category,
                    "description": item.description,
                    "amount": item.amount,
                    "percentage": item.percentage
                })
        
        # Set payment terms if available
        if charter_doc.payment_terms:
            self.payment_terms = charter_doc.payment_terms