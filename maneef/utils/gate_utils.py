import frappe
from frappe import _

GATE_ORDER = {"Gate 1": 1, "Gate 2": 2, "Gate 3": 3}
ALLOWED_ROLES = ["Managing Partner", "System Manager"]


def validate_gate_change(doc, gate_field="custom_gate_status"):
    """
    Shared gate validation for both Project and Project Charter.
    Enforces role restriction and sequential progression.
    Does NOT validate gate criteria (that lives in project_gate_hooks).
    """
    if doc.is_new():
        return

    old_gate = frappe.db.get_value(doc.doctype, doc.name, gate_field)
    new_gate = doc.get(gate_field)

    if old_gate == new_gate:
        return

    user_roles = frappe.get_roles(frappe.session.user)
    if not any(r in user_roles for r in ALLOWED_ROLES):
        frappe.throw(_("Only Managing Partner or System Manager can change gate status."))

    old_level = GATE_ORDER.get(old_gate, 0)
    new_level = GATE_ORDER.get(new_gate, 0)
    if new_level > old_level + 1:
        frappe.throw(
            _("Cannot skip gates. Current: {0}. Requested: {1}. Pass each gate sequentially.").format(
                old_gate, new_gate
            )
        )

    frappe.logger().info(
        "Gate status change: doctype=%s name=%s from=%s to=%s user=%s",
        doc.doctype, doc.name, old_gate, new_gate, frappe.session.user,
    )
