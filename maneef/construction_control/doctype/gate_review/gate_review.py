import frappe
from frappe import _
from frappe.model.document import Document
from maneef.utils.gate_utils import validate_gate_change


class GateReview(Document):
    def validate(self):
        self._validate_no_duplicate_pending()

    def on_submit(self):
        if self.decision == "Approved":
            self._apply_gate_to_project()

    def _validate_no_duplicate_pending(self):
        if self.is_new():
            return
        existing = frappe.db.get_value(
            "Gate Review",
            {
                "project": self.project,
                "gate": self.gate,
                "docstatus": 0,
                "name": ["!=", self.name],
            },
            "name",
        )
        if existing:
            frappe.throw(
                _("A pending Gate Review for {0} — {1} already exists: {2}").format(
                    self.project, self.gate, existing
                )
            )

    def _apply_gate_to_project(self):
        project = frappe.get_doc("Project", self.project)
        old_gate = project.custom_gate_status

        gate_order = {"Gate 1": 1, "Gate 2": 2, "Gate 3": 3}
        old_level = gate_order.get(old_gate, 0)
        new_level = gate_order.get(self.gate, 0)

        if new_level <= old_level:
            frappe.throw(
                _("Project is already at {0}. Gate Review for {1} has no effect.").format(
                    old_gate, self.gate
                )
            )

        # Run criteria checks via the same hook logic
        from maneef.design_operations.project_gate_hooks import _validate_gate_criteria
        project.custom_gate_status = self.gate
        _validate_gate_criteria(project)

        frappe.flags.via_gate_review = True
        frappe.db.set_value("Project", self.project, "custom_gate_status", self.gate)
        frappe.flags.via_gate_review = False
        frappe.msgprint(
            _("Project {0} advanced to {1}").format(self.project, self.gate),
            indicator="green",
            alert=True,
        )
