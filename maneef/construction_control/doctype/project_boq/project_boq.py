import frappe
from frappe.model.document import Document

class ProjectBOQ(Document):
    def validate(self):
        self.calculate_totals()
        
    def calculate_totals(self):
        total = 0.0
        for item in self.get('items', []):
            qty = float(item.quantity or 0.0)
            rate = float(item.rate or 0.0)
            item.amount = qty * rate
            total += item.amount
        self.total_amount = total
