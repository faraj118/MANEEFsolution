import frappe
from frappe.model.document import Document

class DurationRiskItem(Document):
    def validate(self):
        self.calculate_score()

    def calculate_score(self):
        scoring = {
            "Expected Duration": {
                "Under 3 months": 1, "3-6 months": 2, "6-12 months": 3,
                "12-18 months": 4, "Over 18 months": 5
            },
            "Cash Flow Gap": {
                "Monthly billing": 1, "Bi-monthly": 2, "Quarterly milestones": 3,
                "End of phase only": 4, "Lump sum on completion": 5
            },
            "Client Decision Speed": {
                "Under 3 days": 1, "1 week": 2, "2-4 weeks": 3,
                "1-2 months": 4, "Over 2 months": 5
            },
            "External Dependencies": {
                "None": 1, "1 dependency (internal)": 2,
                "2 dependencies": 3, "3+ dependencies": 4,
                "Government approvals required": 5
            },
            "Team Lock Duration": {
                "Fully flexible": 1, "Mostly flexible": 2, "Partial lock": 3,
                "Significant lock": 4, "Full lock until completion": 5
            },
            "Scope Creep Probability": {
                "Very low (fixed scope)": 1, "Low": 2, "Medium": 3,
                "High (client-driven changes)": 4, "Very high (T&M, vague)": 5
            },
            "Historical Overrun": {
                "No history or on-time": 1, "Under 10% overrun": 2,
                "10-25% overrun": 3, "25-50% overrun": 4, "Over 50% overrun": 5
            }
        }
        factor_scores = scoring.get(self.risk_factor, {})
        self.risk_score = factor_scores.get(self.factor_value, 0)
