import frappe
from frappe.model.document import Document

class DailyProgressReport(Document):
    def before_save(self):
        self.set_default_site_manager()
        
    def set_default_site_manager(self):
        if not self.site_manager:
            emp = frappe.db.get_value("Employee", {"user_id": frappe.session.user}, "name")
            if emp:
                self.site_manager = emp
