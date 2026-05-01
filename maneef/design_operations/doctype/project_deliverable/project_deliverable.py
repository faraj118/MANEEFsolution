import frappe
from frappe.model.document import Document

class ProjectDeliverable(Document):
    def before_insert(self):
        if not self.project:
            frappe.throw("Project is required for all deliverables")

        # IP Protection: Check signed contract
        contract_status = frappe.db.get_value("Project", self.project, "custom_contract_status")
        if contract_status != "Active":
            frappe.throw("Cannot create deliverables. Project contract status is not Active.")

        # Reset status if amended
        if getattr(self, "amended_from", None):
            self.status = "Draft"

    def validate(self):
        self.check_design_freeze()
        self.check_approval_chain()

    def check_design_freeze(self):
        if self.design_freeze_status == "Frozen":
            if not self.has_value_changed("design_freeze_status"):
                frappe.throw("This deliverable is design-frozen. Create a Change Order to modify.")

    def check_approval_chain(self):
        if self.docstatus == 1:
            return
        if self.doc_controller_issued:
            if not self.principal_approved:
                frappe.throw("Cannot mark as issued. Principal approval is required first.")
            if not self.technical_lead_approved:
                frappe.throw("Cannot mark as issued. Technical Lead approval is required first.")
            if not self.design_lead_approved:
                frappe.throw("Cannot mark as issued. Design Lead approval is required first.")

    def on_submit(self):
        self.status = "Issued"

    def on_cancel(self):
        self.status = "Superseded"

    @frappe.whitelist()
    def create_new_revision(self):
        if self.docstatus != 1:
            frappe.throw(frappe._("Only submitted deliverables can be revised."))
        new_doc = frappe.copy_doc(self)
        
        curr_rev = self.revision or ""
        if not curr_rev:
            new_rev = "1"
        elif curr_rev.isdigit():
            new_rev = str(int(curr_rev) + 1)
        elif curr_rev.startswith("R") and curr_rev[1:].isdigit():
            new_rev = f"R{int(curr_rev[1:]) + 1}"
        elif len(curr_rev) == 1 and curr_rev.isalpha():
            new_rev = chr(ord(curr_rev) + 1)
        else:
            new_rev = curr_rev + "-1"
            
        new_doc.revision = new_rev
        new_doc.status = "Draft"
        new_doc.amended_from = self.name
        new_doc.insert(ignore_permissions=False)
        frappe.msgprint(frappe._("New revision created: {0}").format(new_doc.name), alert=True)
        return new_doc.name
