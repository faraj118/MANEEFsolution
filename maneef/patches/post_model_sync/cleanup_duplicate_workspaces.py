import frappe


def execute():
    stale = ["aec-architecture-square", "aec_architecture_square", "Maneef GM Command"]
    for name in stale:
        if frappe.db.exists("Workspace", name):
            frappe.db.delete("Workspace", {"name": name})
    frappe.db.commit()
