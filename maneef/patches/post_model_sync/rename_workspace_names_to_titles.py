import frappe


def execute():
    stale = [
        "commercial-bidding",
        "design-documentation",
        "construction-control-ws",
        "financial-control-ws",
        "maneef-gm-command",
    ]
    for name in stale:
        if frappe.db.exists("Workspace", name):
            frappe.db.delete("Workspace", {"name": name})
    frappe.db.commit()
