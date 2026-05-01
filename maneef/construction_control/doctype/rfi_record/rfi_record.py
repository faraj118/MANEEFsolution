import frappe
from frappe.model.document import Document
from frappe import _

class RfiRecord(Document):
    def validate(self):
        if not getattr(self, "is_billable", True):
            allowed_roles = ["Project Manager", "Managing Partner", "System Manager"]
            user_roles = frappe.get_roles(frappe.session.user)
            if not any(r in user_roles for r in allowed_roles):
                frappe.throw("Only Project Manager or above can mark an RFI as non-billable")
            if not self.get("non_billable_justification"):
                frappe.throw("Justification is required when marking RFI as non-billable")

        self.check_variation_impact()

    def check_variation_impact(self):
        if self.has_cost_impact or self.has_schedule_impact:
            # We enforce that if an RFI has impact, a Variation Order isn't technically strictly required immediately upon saving,
            # but we can optionally flag the PM. For now, just log an info message.
            if not getattr(self, '__variation_warning_shown', False):
                frappe.msgprint(
                    _("This RFI has marked Schedule/Cost impact. Please ensure a <b>Project Variation Order</b> is raised against Project {0} to amend the contracted fees or schedule.").format(self.project),
                    indicator="orange",
                    alert=True
                )
                self.__variation_warning_shown = True

def weekly_open_items_report():
    open_rfis = frappe.db.count("RFI Record", {"status": "Open", "has_cost_impact": 1})
    if open_rfis:
        mps = frappe.get_all("Has Role", filters={"role": "Managing Partner"}, pluck="parent")
        if mps:
            frappe.sendmail(recipients=mps, subject=_("Open High-Impact RFIs"), message=_("There are {0} open RFIs with commercial impact.").format(open_rfis))
