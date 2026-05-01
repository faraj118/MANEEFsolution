import frappe
from frappe.model.document import Document

class PaymentRiskScanItem(Document):
    def validate(self):
        self.calculate_score()

    def calculate_score(self):
        scoring = {
            "Funding Source": {
                "Government": 1, "Bank-financed": 2, "Private (established)": 2,
                "Private (new)": 4, "Self-funded (individual)": 5
            },
            "Payment History": {
                "New client": 3, "Reliable (3+ projects)": 1, "Mostly reliable": 2,
                "Delayed (past issues)": 4, "Defaulted": 5
            },
            "Budget Realism": {
                "Realistic": 1, "Slightly optimistic": 2, "Optimistic": 3,
                "Unrealistic": 4, "Unknown": 5
            },
            "Contract Type": {
                "Lump Sum": 1, "Percentage of Construction": 2,
                "Time and Materials": 3, "Cost Plus": 4, "No contract yet": 5
            },
            "Payment Terms": {
                "Monthly": 1, "Bi-monthly": 2, "Milestone-based": 3,
                "End of phase": 4, "On-demand / unclear": 5
            },
            "Payment Security": {
                "Bank Guarantee": 1, "Letter of Credit": 1,
                "Post-dated Cheques": 2, "Cheque on delivery": 3, "None": 5
            }
        }
        factor_scores = scoring.get(self.risk_factor, {})
        self.risk_score = factor_scores.get(self.factor_value, 0)
