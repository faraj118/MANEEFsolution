import frappe
from frappe import _
from maneef.utils.gate_utils import validate_gate_change


def validate_project_gate_status(doc, method):
    validate_gate_change(doc)
    _require_gate_review(doc)
    _validate_gate_criteria(doc)


def _require_gate_review(doc):
    """Block direct gate changes unless an approved Gate Review exists."""
    if doc.is_new():
        return
    old_gate = frappe.db.get_value("Project", doc.name, "custom_gate_status")
    if old_gate == doc.custom_gate_status:
        return
    # Allow if triggered programmatically from GateReview.on_submit
    if frappe.flags.get("via_gate_review"):
        return
    settings = frappe.get_single("Maneef Settings")
    if not settings.gate_review_required:
        return
    approved = frappe.db.exists(
        "Gate Review",
        {"project": doc.name, "gate": doc.custom_gate_status, "decision": "Approved", "docstatus": 1},
    )
    if not approved:
        frappe.throw(
            _("Gate status cannot be changed directly. Create and submit an approved Gate Review for {0}.").format(
                doc.custom_gate_status
            )
        )


def _validate_gate_criteria(doc):
    if doc.is_new():
        return

    old_gate = frappe.db.get_value("Project", doc.name, "custom_gate_status")
    if old_gate == doc.custom_gate_status:
        return

    if doc.custom_gate_status == "Gate 2":
        _validate_gate_1_criteria(doc)
    elif doc.custom_gate_status == "Gate 3":
        _validate_gate_2_criteria(doc)


def _validate_gate_1_criteria(doc):
    charter = None
    if doc.custom_project_charter:
        charter = frappe.get_doc("Project Charter", doc.custom_project_charter)
    elif doc.sales_order:
        so = frappe.get_doc("Sales Order", doc.sales_order)
        if so.custom_project_charter:
            charter = frappe.get_doc("Project Charter", so.custom_project_charter)

    if not charter:
        frappe.throw(_("Cannot advance to Gate 2. No Project Charter linked."))

    if charter.go_no_go_decision != "GO":
        frappe.throw(_("Cannot advance to Gate 2. GO/NO-GO decision is not GO."))

    if charter.linked_risk_assessment:
        ra = frappe.get_doc("Risk Assessment", charter.linked_risk_assessment)
        if ra.payment_risk_rating == "Unacceptable":
            frappe.throw(_("Cannot advance to Gate 2. Payment Risk is Unacceptable."))
        if ra.commercial_risk_rating == "Red":
            frappe.throw(_("Cannot advance to Gate 2. Commercial Risk is Red."))
        if ra.overall_risk_rating == "Critical":
            frappe.throw(_("Cannot advance to Gate 2. Overall Risk is Critical. Managing Partner must override."))
    else:
        if charter.custom_payment_risk_rating == "Unacceptable":
            frappe.throw(_("Cannot advance to Gate 2. Payment Risk is Unacceptable."))
        if charter.custom_commercial_risk_rating == "Red":
            frappe.throw(_("Cannot advance to Gate 2. Commercial Risk is Red."))

    contract_status = None
    if charter.sales_order:
        contract_status = frappe.db.get_value("Sales Order", charter.sales_order, "custom_contract_status")
    if contract_status != "Signed":
        frappe.throw(_("Cannot advance to Gate 2. Contract is not Signed."))


def _validate_gate_2_criteria(doc):
    if not frappe.db.exists("Task", {
        "project": doc.name,
        "custom_task_type": "Project Management",
        "status": ["!=", "Cancelled"]
    }):
        frappe.throw(_("Cannot advance to Gate 3. No Project Management plan found."))

    if not doc.expected_start_date or not doc.expected_end_date:
        frappe.throw(_("Cannot advance to Gate 3. Project schedule (start/end dates) is not set."))
