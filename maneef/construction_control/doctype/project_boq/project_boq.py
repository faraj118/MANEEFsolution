import frappe
from frappe.model.document import Document

class ProjectBOQ(Document):
    def validate(self):
        if self.docstatus == 1 or self.flags.in_insert:
            has_rds = frappe.db.exists("BOQ Room Data Sheet Link", {"parent": self.name})
            if not has_rds and not getattr(self, "room_data_sheet", None):
                frappe.throw("BOQ must be linked to at least one Room Data Sheet before submission")
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
