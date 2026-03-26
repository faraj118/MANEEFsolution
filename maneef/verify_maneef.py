import frappe

def verify_setup():
    # No frappe.init or frappe.connect needed here! bench execute handles it.
    
    print("--- 🛡️ AEC Workflow Check ---")
    wf_name = "Maneef Deliverable Approval"
    if frappe.db.exists("Workflow", wf_name):
        wf = frappe.get_doc("Workflow", wf_name)
        print(f"✅ Workflow '{wf_name}' exists and is {'ACTIVE' if wf.is_active else 'INACTIVE'}")
        print(f"   Target DocType: {wf.document_type}")
    else:
        print(f"❌ Workflow '{wf_name}' NOT FOUND")
        
    print("\n--- ⚡ Workflow Actions Check ---")
    actions = ["Submit for Review", "Escalate to GM", "Return to Production", "Re-submit", "Approve", "Reject"]
    for action in actions:
        if frappe.db.exists("Workflow Action", action):
            print(f"✅ Action '{action}' registered")
        else:
            print(f"❌ Action '{action}' MISSING")
            
    print("\n--- 🚨 Error Log Check (Recent Maneef) ---")
    
    # Dynamically detect fields to avoid 'Unknown column' errors on different Frappe versions
    meta = frappe.get_meta("Error Log")
    fields = [f.fieldname for f in meta.fields]
    
    # Try to find a 'title' or 'method' or 'subject' field for identification
    ident_field = None
    for f in ["method", "title", "subject"]:
        if f in fields:
            ident_field = f
            break
            
    if not ident_field:
        print("ℹ️ Could not find a title/method field in Error Log. Skipping detailed log check.")
        return

    from frappe.utils import add_to_date
    try:
        errors = frappe.get_all("Error Log", filters={
            ident_field: ["like", f"%Maneef%"],
            "creation": [">", add_to_date(None, hours=-1)]
        }, fields=[ident_field], order_by="creation desc", limit=5)
        
        if errors:
            for err in errors:
                print(f"⚠️ Logged: {err.get(ident_field)}")
        else:
            print("✅ No recent Maneef errors in the last hour.")
    except Exception as e:
        print(f"ℹ️ Error Log Check encountered a non-critical issue: {str(e)}")
