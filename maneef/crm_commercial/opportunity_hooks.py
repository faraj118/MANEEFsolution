import frappe

from frappe import _

def validate(doc, method=None):
    if doc.status == "Quotation" and not frappe.db.exists("Commercial Risk Review", {"opportunity": doc.name}):
        frappe.msgprint(_("Warning: Commercial Risk Review should be completed before reaching Quotation stage."), indicator="orange")


def on_update(doc, method=None):
    if doc.status == "Lost":
        charters = frappe.get_all("Project Charter", filters={"opportunity": doc.name, "docstatus": 0})
        for c in charters:
            frappe.db.set_value("Project Charter", c.name, "status", "Abandoned")
