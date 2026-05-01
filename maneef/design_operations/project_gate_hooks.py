import frappe

def validate_project_gate_status(doc, method):
    if doc.is_new():
        return

    old_gate = frappe.db.get_value("Project", doc.name, "custom_gate_status")
    if old_gate == doc.custom_gate_status:
        return

    allowed_roles = ["Managing Partner", "System Manager"]
    user_roles = frappe.get_roles(frappe.session.user)
    if not any(r in user_roles for r in allowed_roles):
        frappe.throw("Only Managing Partner or System Manager can change gate status")

    gate_order = {"Gate 1": 1, "Gate 2": 2, "Gate 3": 3}
    old_level = gate_order.get(old_gate, 0)
    new_level = gate_order.get(doc.custom_gate_status, 0)
    if new_level > old_level + 1:
        frappe.throw(f"Cannot skip gates. Current: {old_gate}. Requested: {doc.custom_gate_status}. Pass each gate sequentially.")

    # Gate criteria validation
    if doc.custom_gate_status == "Gate 2":
        validate_gate_1_criteria(doc)
    elif doc.custom_gate_status == "Gate 3":
        validate_gate_2_criteria(doc)

    frappe.logger().info(
        "Gate status change: project=%s from=%s to=%s user=%s",
        doc.name, old_gate, doc.custom_gate_status, frappe.session.user
    )

def validate_gate_1_criteria(doc):
    charter = None
    if doc.custom_project_charter:
        charter = frappe.get_doc("Project Charter", doc.custom_project_charter)
    elif doc.sales_order:
        so = frappe.get_doc("Sales Order", doc.sales_order)
        if so.custom_project_charter:
            charter = frappe.get_doc("Project Charter", so.custom_project_charter)

    if not charter:
        frappe.throw("Cannot advance to Gate 2. No Project Charter linked.")

    if charter.go_no_go_decision != "GO":
        frappe.throw("Cannot advance to Gate 2. GO/NO-GO decision is not GO.")

    # Check Risk Assessment
    if charter.linked_risk_assessment:
        ra = frappe.get_doc("Risk Assessment", charter.linked_risk_assessment)

        if ra.payment_risk_rating == "Unacceptable":
            frappe.throw("Cannot advance to Gate 2. Risk Assessment Payment Risk is Unacceptable.")

        if ra.commercial_risk_rating == "Red":
            frappe.throw("Cannot advance to Gate 2. Risk Assessment Commercial Risk is Red.")

        if ra.overall_risk_rating == "Critical":
            frappe.throw("Cannot advance to Gate 2. Overall Risk Assessment is Critical. Managing Partner must override.")
    else:
        # Fallback to charter child table ratings
        if charter.custom_payment_risk_rating == "Unacceptable":
            frappe.throw("Cannot advance to Gate 2. Payment Risk is Unacceptable.")

        if charter.custom_commercial_risk_rating == "Red":
            frappe.throw("Cannot advance to Gate 2. Commercial Risk is Red.")

    # Check contract
    contract_status = None
    if charter.sales_order:
        contract_status = frappe.db.get_value("Sales Order", charter.sales_order, "custom_contract_status")
    if contract_status != "Signed":
        frappe.throw("Cannot advance to Gate 2. Contract is not Signed.")

def validate_gate_2_criteria(doc):
    pm_plan_exists = frappe.db.exists("Task", {
        "project": doc.name,
        "custom_task_type": "Project Management",
        "status": ["!=", "Cancelled"]
    })
    if not pm_plan_exists:
        frappe.throw("Cannot advance to Gate 3. No Project Management plan found.")

    if not doc.expected_start_date or not doc.expected_end_date:
        frappe.throw("Cannot advance to Gate 3. Project schedule (start/end dates) is not set.")
