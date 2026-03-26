import frappe
from frappe.model.document import Document
from frappe import _

class RfiRecord(Document):
    def before_insert(self):
        self.is_billable = 1

    def validate(self):
        self._enforce_billable_override_rules()

    def before_submit(self):
        self._require_change_order_for_design_change()

    def _enforce_billable_override_rules(self):
        if not self.is_billable:
            user_roles = frappe.get_roles(frappe.session.user)
            allowed = any(r in user_roles for r in ["Project Manager", "Managing Partner", "System Manager"])
            if not allowed:
                frappe.throw(_("Only a Project Manager, Managing Partner, or System Manager can mark an RFI as non-billable."))
            if not self.nonbillable_justification:
                frappe.throw(_("A justification is required for non-billable RFIs."))
            self.pm_override_by = frappe.session.user

    def _require_change_order_for_design_change(self):
        if self.response_type == "Design Change (Billable)" and not self.linked_change_order:
            frappe.throw(_("A Change Order must be raised before submitting a Design Change (Billable) RFI."))

def weekly_open_items_report():
    open_billable = frappe.db.count("RFI Record", {"is_billable": 1, "status": "Open"})
    if open_billable:
        mps = frappe.get_all("Has Role", filters={"role": "Managing Partner"}, pluck="parent")
        if mps:
            frappe.sendmail(recipients=mps, subject="Open Billable RFIs", message=f"There are {open_billable} open billable RFIs.")
