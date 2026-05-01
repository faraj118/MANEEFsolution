import frappe
from maneef.utils.deletion_guard import protect_deletion


def validate_customer_deletion(doc, method):
    protect_deletion(doc, [
        {"doctype": "Project Charter", "link_field": "customer", "label": "Project Charters"},
        {"doctype": "Project", "link_field": "customer", "label": "Projects"},
        {"doctype": "Project BOQ", "link_field": "customer", "label": "Project BOQs"},
        {"doctype": "Site Visit Report", "link_field": "customer", "label": "Site Visit Reports"},
        {"doctype": "SVR Issue", "link_field": "customer", "label": "SVR Issues"},
    ])
