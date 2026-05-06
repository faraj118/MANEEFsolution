import frappe
from maneef.utils.deletion_guard import protect_deletion

from frappe import _

def before_submit(doc, method=None):
    if not doc.custom_charter_approved:
        frappe.throw(_("Project Charter must be approved before submitting Sales Order."))



def validate_sales_order_deletion(doc, method):
    protect_deletion(doc, [
        {"doctype": "Project Charter", "link_field": "sales_order", "label": "Project Charters"},
    ])
