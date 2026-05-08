import frappe
from frappe.model.document import Document


class SnagList(Document):
    def validate(self):
        self._update_counts()

    def _update_counts(self):
        snags = self.get("snags", [])
        self.open_critical_count = sum(
            1 for s in snags
            if s.status in ("Open", "In Progress") and s.priority == "Critical"
        )
        self.total_open_count = sum(
            1 for s in snags if s.status in ("Open", "In Progress")
        )
