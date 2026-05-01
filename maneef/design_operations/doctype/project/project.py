import frappe
from frappe.model.document import Document

class Project(Document):
    def validate(self):
        self.validate_gate_status_change()

    def validate_gate_status_change(self):
        if not self.is_new():
            old_gate = frappe.db.get_value("Project", self.name, "custom_gate_status")
            if old_gate != self.custom_gate_status:
                allowed_roles = ["Managing Partner", "System Manager"]
                user_roles = frappe.get_roles(frappe.session.user)
                if not any(r in user_roles for r in allowed_roles):
                    frappe.throw("Only Managing Partner or System Manager can change gate status")

                # Enforce sequential gates
                gate_order = {"Gate 1": 1, "Gate 2": 2, "Gate 3": 3}
                old_level = gate_order.get(old_gate, 0)
                new_level = gate_order.get(self.custom_gate_status, 0)
                if new_level > old_level + 1:
                    frappe.throw(f"Cannot skip gates. Current: {old_gate}. Requested: {self.custom_gate_status}. Pass each gate sequentially.")

                frappe.logger().info(
                    "Gate status change: project=%s from=%s to=%s user=%s",
                    self.name, old_gate, self.custom_gate_status, frappe.session.user
                )