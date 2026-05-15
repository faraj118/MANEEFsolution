import frappe
from frappe.model.document import Document
from frappe import _

class SubcontractorValuation(Document):
    def before_insert(self):
        if not self.retention_pct:
            settings = frappe.get_single("Company Settings")
            self.retention_pct = settings.default_retention_pct or 10

    def validate(self):
        from frappe.utils import flt
        total = 0.0
        for item in self.get('items', []):
            current_pct = flt(item.current_claim_pct)
            prev_pct = flt(item.previously_claimed_pct)
            
            if current_pct > 100:
                frappe.throw(_("Current claim cannot exceed 100% on a single valuation line for Item {0}.").format(item.item_code))
                
            if flt(prev_pct + current_pct, 2) > 100.0:
                frappe.throw(_("Cumulative claim exceeds 100% for Item {0}.").format(item.item_code))
                
            # Calculation: (Rate × BOQ Qty) × Claim %
            rate = flt(item.rate)
            qty = flt(item.boq_quantity)
            
            amount_claimed = (rate * qty) * (current_pct / 100.0)
            item.claimed_amount = flt(amount_claimed, 2)
            total += item.claimed_amount
            
        self.total_claimed_amount = flt(total, 2)
        
        # Apply standard construction retention holdback
        retention = total * (flt(self.retention_pct) / 100.0)
        self.net_payable = flt(total - retention, 2)
