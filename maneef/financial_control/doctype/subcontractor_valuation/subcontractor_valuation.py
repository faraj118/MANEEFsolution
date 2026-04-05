import frappe
from frappe.model.document import Document
from frappe import _

class SubcontractorValuation(Document):
    def validate(self):
        total = 0.0
        for item in self.get('items', []):
            current_pct = item.current_claim_pct or 0.0
            prev_pct = item.previously_claimed_pct or 0.0
            
            if current_pct > 100:
                frappe.throw(_("Current claim cannot exceed 100% on a single valuation line for Item {0}.").format(item.item_code))
                
            if prev_pct + current_pct > 100 + 0.01: # Small tolerance for float drift
                frappe.throw(_("Cumulative claim exceeds 100% for Item {0}.").format(item.item_code))
                
            # Calculation: (Rate × BOQ Qty) × Claim %
            rate = float(item.rate or 0.0)
            qty = float(item.boq_quantity or 0.0)
            
            amount_claimed = (rate * qty) * (current_pct / 100.0)
            item.claimed_amount = amount_claimed
            total += amount_claimed
            
        self.total_claimed_amount = total
        
        # Apply standard construction retention holdback
        retention = total * (float(self.retention_pct or 0.0) / 100.0)
        self.net_payable = total - retention
