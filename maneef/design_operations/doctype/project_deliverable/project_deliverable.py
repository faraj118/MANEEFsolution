_REVISIONS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_DISC_CODE = {"Architecture":"A","Interior":"I","Landscape":"L","Structure":"S","MEP":"M","BIM":"B"}
_LOD_ORDER = ["LOD 100","LOD 200","LOD 300","LOD 400","LOD 500"]
_MAX_LOD = {"Innovation Projects":"LOD 200","Landscape Projects":"LOD 300",
           "Small Construction":"LOD 300","Medium Construction":"LOD 300",
           "Large Construction":"LOD 400","Complex Construction":"LOD 500"}

import frappe
from frappe.model.document import Document

class ProjectDeliverable(Document):
    def before_insert(self):
        self._enforce_ip_lock()
        self._auto_generate_drawing_id()
        self._assign_first_revision()

    def before_save(self):
        self._handle_revision_on_new_upload()
        self._sync_client_visibility()

    def validate(self):
        self._validate_bim_lod()
        self._validate_stop_work_not_active()

    def _enforce_ip_lock(self):
        if not frappe.db.exists("Sales Order", {"project": self.project, "custom_contract_status": ["in", ["Signed", "Active"]], "docstatus": 1}):
            frappe.throw("IP Protection Lock (BR-01): No signed or active contract for this project.")

    def _auto_generate_drawing_id(self):
        if not self.drawing_id:
            seq = frappe.db.count("Project Deliverable", {"project": self.project, "discipline": self.discipline}) + 1
            disc = _DISC_CODE.get(self.discipline, "X")
            self.drawing_id = f"AS-{self.project}-{disc}-{seq:03d}"

    def _assign_first_revision(self):
        if not self.revision_no:
            self.revision_no = "A"

    def _handle_revision_on_new_upload(self):
        if not self.is_new() and self.drawing_id and self.file_attachment:
            prev = frappe.get_all("Project Deliverable", filters={"drawing_id": self.drawing_id, "name": ["!=", self.name]}, order_by="creation DESC", limit=1)
            if prev:
                prev_doc = frappe.get_doc("Project Deliverable", prev[0]["name"])
                idx = _REVISIONS.index(prev_doc.revision_no) if prev_doc.revision_no in _REVISIONS else 0
                new_rev = _REVISIONS[idx+1] if idx+1 < len(_REVISIONS) else prev_doc.revision_no
                self.previous_revision = prev_doc.name
                frappe.db.set_value("Project Deliverable", prev_doc.name, {"status": "Superseded", "superseded_by": self.name, "client_visible": 0})
                self.revision_no = new_rev

    def _sync_client_visibility(self):
        self.client_visible = 1 if self.status == "Issued" else 0

    def _validate_bim_lod(self):
        project_type = frappe.db.get_value("Project", self.project, "custom_project_type")
        max_lod = _MAX_LOD.get(project_type)
        if max_lod and self.bim_lod and self.bim_lod in _LOD_ORDER and _LOD_ORDER.index(self.bim_lod) > _LOD_ORDER.index(max_lod):
            frappe.throw(f"LOD {self.bim_lod} exceeds max allowed {max_lod} for project type {project_type}.")

    def _validate_stop_work_not_active(self):
        if frappe.db.get_value("Project", self.project, "custom_stop_work_active"):
            frappe.throw("Cannot modify deliverable while Stop Work is active on this project.")

    @frappe.whitelist()
    def create_new_revision(self):
        new_doc = frappe.copy_doc(self)
        new_doc.name = None
        new_doc.status = "Draft"
        new_doc.issued_by = None
        new_doc.revision_no = None
        new_doc.insert(ignore_permissions=True)
        return {"status": "success", "message": "Revision created", "new_name": new_doc.name}