import frappe
from frappe import _

def before_submit(doc, method=None):
    if not doc.custom_is_payment_certificate:
        return
    contractor = doc.custom_contractor
    project = doc.custom_project
    if not contractor or not project:
        return
    snags = frappe.get_all("Issue", filters={
        "custom_project": project,
        "custom_contractor": contractor,
        "priority": ["in", ["High", "Critical"]],
        "status": ["!=", "Resolved"]
    }, fields=["name", "subject", "priority"])
    if snags:
        snag_list = ", ".join(["{0} ({1})".format(s["name"], s["priority"]) for s in snags])
        frappe.throw(_("Payment Certificate Blocked (BRD Section 7). Open snags: {0}. All High and Critical snags must be Resolved before payment can be released.").format(snag_list))
