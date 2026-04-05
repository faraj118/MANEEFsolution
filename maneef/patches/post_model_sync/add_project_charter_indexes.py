def execute():
    """Add database indexes for Project Charter performance optimization"""
    import frappe
    
    # Indexes for Project Charter
    indexes = [
        {
            "doctype": "Project Charter",
            "fields": ["project", "customer"]
        },
        {
            "doctype": "Project Charter",
            "fields": ["status", "docstatus"]
        },
        {
            "doctype": "Project Charter",
            "fields": ["start_date", "end_date"]
        },
        {
            "doctype": "Project Charter",
            "fields": ["project_priority", "risk_level"]
        }
    ]
    
    for index in indexes:
        try:
            frappe.db.add_index(index["doctype"], index["fields"])
        except Exception as e:
            frappe.log_error(f"Failed to create index on {index['doctype']} {index['fields']}: {str(e)}")