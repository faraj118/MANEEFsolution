import frappe
from frappe.model.document import Document
from frappe import _

class SVRPhoto(Document):
    def validate(self):
        if self.photo_file and not self.caption:
            frappe.msgprint(_("Please add a caption describing what this photo shows."))
