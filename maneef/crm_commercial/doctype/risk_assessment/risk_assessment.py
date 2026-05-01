import frappe
from frappe.model.document import Document

class RiskAssessment(Document):
    def validate(self):
        self.auto_populate_from_linked_records()
        self.calculate_risk_totals()
        self.calculate_overall_risk()
        self.generate_recommendations()

    def auto_populate_from_linked_records(self):
        # Pull customer payment history
        if self.customer:
            past_projects = frappe.db.count("Project", {
                "customer": self.customer,
                "status": ["in", ["Open", "Closed"]]
            })
            self.customer_project_count = past_projects

            # Check for overdue invoices on this customer
            overdue = frappe.db.count("Sales Invoice", {
                "customer": self.customer,
                "status": "Overdue"
            })
            self.customer_overdue_invoices = overdue

        # Pull project performance data
        if self.project:
            # Burn rate
            burn = frappe.db.get_value("Project", self.project, "custom_burn_percentage") or 0
            self.project_burn_percentage = burn

            # Contracted fee
            fee = frappe.db.get_value("Project", self.project, "custom_contracted_fee") or 0
            self.project_contracted_fee = fee

            # Open RFIs count
            open_rfi_count = frappe.db.count("RFI Record", {
                "project": self.project,
                "docstatus": 1,
                "status": ["in", ["Open", "Overdue"]]
            })
            self.project_open_rfis = open_rfi_count

            # Open snags count
            open_snag_count = frappe.db.count("SVR Issue", {
                "project": self.project,
                "status": ["!=", "Closed"]
            })
            self.project_open_snags = open_snag_count

        # Pull charter data
        if self.project_charter:
            charter = frappe.get_doc("Project Charter", self.project_charter)
            self.go_no_go_decision = charter.go_no_go_decision or ""
            if charter.sales_order:
                contract = frappe.db.get_value("Sales Order", charter.sales_order, "custom_contract_status")
                self.contract_status = contract or ""

    def calculate_risk_totals(self):
        # Payment Risk
        payment_items = self.get("payment_risk_items", [])
        if payment_items:
            total = sum(item.risk_score for item in payment_items)
            self.total_payment_risk_score = total
            if total <= 7:
                self.payment_risk_rating = "Low"
            elif total <= 14:
                self.payment_risk_rating = "Medium"
            elif total <= 21:
                self.payment_risk_rating = "High"
            else:
                self.payment_risk_rating = "Unacceptable"

        # Commercial Risk
        commercial_items = self.get("commercial_risk_items", [])
        if commercial_items:
            total = sum(item.risk_score for item in commercial_items)
            self.total_commercial_risk_score = total
            if total <= 10:
                self.commercial_risk_rating = "Green"
            elif total <= 20:
                self.commercial_risk_rating = "Amber"
            else:
                self.commercial_risk_rating = "Red"

        # Duration Risk
        duration_items = self.get("duration_risk_items", [])
        if duration_items:
            total = sum(item.risk_score for item in duration_items)
            self.total_duration_risk_score = total
            if total <= 7:
                self.duration_risk_rating = "Green"
            elif total <= 14:
                self.duration_risk_rating = "Amber"
            elif total <= 21:
                self.duration_risk_rating = "Red"
            else:
                self.duration_risk_rating = "Critical"

    def calculate_overall_risk(self):
        ratings = []
        rating_scores = {
            "Low": 1, "Green": 1,
            "Medium": 2, "Amber": 2,
            "High": 3, "Red": 3,
            "Unacceptable": 4, "Critical": 4
        }

        if self.payment_risk_rating:
            ratings.append(rating_scores.get(self.payment_risk_rating, 0))
        if self.commercial_risk_rating:
            ratings.append(rating_scores.get(self.commercial_risk_rating, 0))
        if self.duration_risk_rating:
            ratings.append(rating_scores.get(self.duration_risk_rating, 0))

        if ratings:
            avg = sum(ratings) / len(ratings)
            self.overall_risk_score = round(avg, 1)
            if avg <= 1.5:
                self.overall_risk_rating = "Low"
            elif avg <= 2.5:
                self.overall_risk_rating = "Medium"
            elif avg <= 3.5:
                self.overall_risk_rating = "High"
            else:
                self.overall_risk_rating = "Critical"

    def generate_recommendations(self):
        recommendations = []

        # Payment risk recommendations
        if self.customer_overdue_invoices and self.customer_overdue_invoices > 0:
            recommendations.append("CRITICAL: Customer has {0} overdue invoice(s). Require advance payment or bank guarantee.".format(self.customer_overdue_invoices))

        if self.payment_risk_rating == "Unacceptable":
            recommendations.append("CRITICAL: Payment risk is unacceptable. Do not proceed without Managing Partner written override.")

        # Commercial risk recommendations
        if self.commercial_risk_rating == "Red":
            recommendations.append("CRITICAL: Commercial risk is Red. Review fee proposal and minimum acceptable fee before proceeding.")

        # Duration risk recommendations
        if self.duration_risk_rating in ("Red", "Critical"):
            recommendations.append("WARNING: Duration risk is high. Add 10-25% duration contingency to fee proposal.")

        # Burn rate warnings
        if self.project_burn_percentage and self.project_burn_percentage >= 80:
            recommendations.append("WARNING: Project burn rate is {0}%. Review stage fee allocation.".format(self.project_burn_percentage))

        # Open issues
        if self.project_open_rfis and self.project_open_rfis > 5:
            recommendations.append("WARNING: {0} open RFIs. Consider monthly invoice for outstanding RFIs.".format(self.project_open_rfis))

        if self.project_open_snags and self.project_open_snags > 3:
            recommendations.append("WARNING: {0} open snags. Payment Certificates may be blocked.".format(self.project_open_snags))

        self.risk_recommendations = "\n".join(recommendations) if recommendations else "No critical recommendations at this time."
