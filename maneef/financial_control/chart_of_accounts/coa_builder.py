import frappe
import json
import os
from frappe import _

@frappe.whitelist()
def check_coa_compliance(company):
    """Checks if the Maneef AEC accounts exist for the company."""
    critical_accounts = [
        "1150 Work in Progress - WIP (Projects) | أعمال تحت التنفيذ - WIP",
        "5110 Project Salaries Allocation | توزيع رواتب المشاريع"
    ]
    abbr = frappe.db.get_value("Company", company, "abbr")
    if not abbr:
        return {"error": "Company not found"}
        
    missing = []
    for acc in critical_accounts:
        if not frappe.db.exists("Account", f"{acc} - {abbr}"):
            missing.append(acc)
    
    return {
        "is_compliant": len(missing) == 0,
        "missing_accounts": missing
    }

@frappe.whitelist()
def setup_maneef_coa(company):
    if not frappe.has_permission("Company", "write", company):
        frappe.throw(_("Not permitted"))

    json_path = os.path.join(frappe.get_app_path("maneef"), "financial_control", "chart_of_accounts", "maneef_aec_coa.json")
    with open(json_path, "r", encoding="utf-8") as f:
        coa = json.load(f)

    # Validate company exists and get its abbreviation
    abbr = frappe.db.get_value("Company", company, "abbr")
    if not abbr:
        frappe.throw(_("Company {0} not found.").format(company))

    def create_account(account_name, parent_account=None, account_data=None):
        account_id = f"{account_name} - {abbr}"
        if frappe.db.exists("Account", account_id):
            return account_id
            
        doc = frappe.new_doc("Account")
        doc.account_name = account_name
        doc.company = company
        doc.parent_account = parent_account
        doc.is_group = account_data.get("is_group", 0)
        
        if parent_account is None:
            # It's a root
            doc.report_type = account_data.get("report_type")
            doc.root_type = account_data.get("root_type")
            
        if account_data.get("account_type"):
            doc.account_type = account_data.get("account_type")
            
        doc.insert(ignore_permissions=True)
        return account_id

    def traverse_tree(tree, parent=None):
        for acc_name, data in tree.items():
            if acc_name in ["account_type", "is_group", "root_type", "report_type"]:
                continue
            
            # Extract data
            acc_data = {
                "is_group": data.get("is_group", 0)
            }
            if "account_type" in data:
                acc_data["account_type"] = data["account_type"]
            if "root_type" in data:
                acc_data["root_type"] = data["root_type"]
            if "report_type" in data:
                acc_data["report_type"] = data["report_type"]
                
            account_id = create_account(acc_name, parent, acc_data)
            
            # Recursive children
            children_tree = {k: v for k, v in data.items() if isinstance(v, dict)}
            if children_tree:
                traverse_tree(children_tree, account_id)

    traverse_tree(coa["tree"])
    frappe.msgprint(_("Maneef Chart of Accounts successfully setup for company '{0}'.").format(company))
    return {"status": "success", "message": f"Setup complete for {company}."}
