import frappe
from frappe.model.document import Document

class CommercialRiskItem(Document):
    def validate(self):
        self.calculate_score()

    def calculate_score(self):
        scoring = {
            "Margin Analysis": {
                "Above 30%": 1, "20-30%": 2, "10-20%": 3,
                "5-10%": 4, "Below 5% or negative": 5
            },
            "Scope Clarity": {
                "Crystal clear, detailed brief": 1, "Mostly clear": 2,
                "Some ambiguity": 3, "Vague": 4, "Undefined": 5
            },
            "Competition Level": {
                "Sole source (invited only)": 1, "Limited competition (2-3)": 2,
                "Competitive (4-6)": 3, "Highly competitive (7+)": 4, "Price war": 5
            },
            "Relationship Value": {
                "Strategic long-term partner": 1, "Recurring client": 2,
                "Second project": 3, "One-time opportunity": 4, "Cold lead": 5
            },
            "Change Order Probability": {
                "Very low (fixed scope)": 1, "Low": 2, "Medium": 3,
                "High (complex project)": 4, "Very high (vague scope)": 5
            },
            "Client Decision Speed": {
                "Under 3 days": 1, "1 week": 2, "2-4 weeks": 3,
                "1-2 months": 4, "Over 2 months": 5
            }
        }
        factor_scores = scoring.get(self.risk_factor, {})
        self.risk_score = factor_scores.get(self.factor_value, 0)
