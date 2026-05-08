import frappe
from frappe.model.document import Document


class Drawing(Document):
    def validate(self):
        self._sync_current_revision()

    def _sync_current_revision(self):
        revisions = self.get("revisions", [])
        if not revisions:
            return
        latest = max(revisions, key=lambda r: r.revision_date or "1900-01-01")
        self.current_revision = latest.revision
