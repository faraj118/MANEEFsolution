import frappe
from maneef.utils.deletion_guard import protect_deletion


def validate_project_deletion(doc, method):
    protect_deletion(doc, [
        {"doctype": "Project BOQ", "link_field": "project", "label": "Project BOQs"},
        {"doctype": "Project BOQ Item", "link_field": "project", "label": "BOQ Items"},
        {"doctype": "Site Visit Report", "link_field": "project", "label": "Site Visit Reports"},
        {"doctype": "SVR Issue", "link_field": "project", "label": "SVR Issues"},
        {"doctype": "RFI Record", "link_field": "project", "label": "RFI Records"},
        {"doctype": "Daily Progress Report", "link_field": "project", "label": "Daily Progress Reports"},
        {"doctype": "Project Budget Control", "link_field": "project", "label": "Budget Controls"},
        {"doctype": "Subcontractor Valuation", "link_field": "project", "label": "Subcontractor Valuations"},
        {"doctype": "Payment Entry", "link_field": "custom_project", "label": "Payment Entries"},
        {"doctype": "Issue", "link_field": "custom_project", "label": "Issues"},
        {"doctype": "Task", "link_field": "project", "label": "Tasks"},
        {"doctype": "Project Variation Order", "link_field": "project", "label": "Variation Orders"},
    ])
