import frappe

def run():
    modules = ["crm_commercial", "design_operations", "construction_control", "financial_control"]
    for m in modules:
        try:
            if frappe.db.exists("Module Def", m):
                frappe.db.delete("Module Def", m)
        except Exception as e:
            print(f"Failed to delete {m}: {e}")
            
    frappe.db.commit()
    print("Orphaned modules cleared successfully! You can now run 'bench --site [site] install-app maneef'")
