import frappe
from frappe.model.document import Document
from frappe import _

class TransmittalDrawings(Document):
    def validate(self):
        if self.project_deliverable:
            status = frappe.db.get_value('Project Deliverable', self.project_deliverable, 'status')
            if status == 'Superseded':
                frappe.msgprint(_(
                    f"Warning: Drawing {self.project_deliverable} has been superseded. Please select the latest revision."), indicator='orange')