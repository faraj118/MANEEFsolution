import frappe
from frappe.model.document import Document

class ProjectBOQ(Document):
    def validate(self):
        self.calculate_totals()
        
    def calculate_totals(self):
        from frappe.utils import flt
        total = 0.0
        for item in self.get('items', []):
            qty = flt(item.quantity)
            rate = flt(item.rate)
            if qty < 0 or rate < 0:
                frappe.throw(f"Quantity and Rate cannot be negative for Item {item.item_code}")
            item.amount = qty * rate
            total += item.amount
        self.total_amount = total
