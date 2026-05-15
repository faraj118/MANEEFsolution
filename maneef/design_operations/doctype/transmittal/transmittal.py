import frappe
from frappe.model.document import Document
from frappe import _

class Transmittal(Document):
    def before_submit(self):
        self._check_doc_controller_role()
        self._validate_all_drawings_issued()
        self._validate_principal_signoff()
        self._set_issue_timestamp()
        self._flag_billing_trigger()

    def on_submit(self):
        self._send_transmittal_email()

    def on_update_after_submit(self):
        if frappe.session.user != "Administrator" and "System Manager" not in frappe.get_roles(frappe.session.user):
            frappe.throw(_("Transmittal {0} is permanently locked. No modifications are permitted after submission.").format(self.name))

    def on_cancel(self):
        frappe.throw(_("Transmittals are permanent legal records and cannot be cancelled."))

    def on_trash(self):
        from maneef.utils.deletion_guard import protect_deletion

        if self.docstatus == 1:
            frappe.throw("Cannot delete a submitted Transmittal. Transmittals are part of the immutable audit trail.")

        protect_deletion(self, [
            {"doctype": "Transmittal Drawings", "link_field": "transmittal", "label": "Transmittal Drawings"},
        ])

    def _check_doc_controller_role(self):
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": ["in", ["Doc Controller", "Managing Partner", "System Manager"]]}):
            frappe.throw(_("You must have Doc Controller, Managing Partner, or System Manager role to submit a Transmittal."))

    def _validate_all_drawings_issued(self):
        non_issued = []
        for d in self.drawings:
            status = frappe.db.get_value("Project Deliverable", d.project_deliverable, "status")
            if not status or status != "Issued":
                non_issued.append(d.project_deliverable)
        if non_issued:
            frappe.throw(_("The following drawings do not exist or are not Issued: {0}").format(", ".join(non_issued)))

    def _validate_principal_signoff(self):
        missing = []
        for d in self.drawings:
            signoff = frappe.db.get_value("Project Deliverable", d.project_deliverable, "principal_approved")
            if not signoff:
                missing.append(d.project_deliverable)
        if missing:
            frappe.throw(_("Principal signoff missing for: {0}").format(", ".join(missing)))

    def _set_issue_timestamp(self):
        self.issue_date = frappe.utils.now()
        self.issued_by = frappe.session.user

    def _flag_billing_trigger(self):
        for d in self.drawings:
            if frappe.db.get_value("Project Deliverable", d.project_deliverable, "custom_is_milestone"):
                self.billing_trigger_active = 1
                break

    def _send_transmittal_email(self):
        if self.recipient_email:
            frappe.sendmail(
                recipients=[self.recipient_email],
                subject=f"Transmittal {self.name}",
                message=f"Please find attached the transmittal {self.name}.<br><br>Issued by {self.issued_by}.",
                attachments=[self._build_pdf_attachment()]
            )

    def _build_pdf_attachment(self):
        pdf = frappe.get_print(self.doctype, self.name, as_pdf=True)
        return {"fname": f"Transmittal_{self.name}.pdf", "fcontent": pdf}

def get_transmittal_drawing_list(transmittal_name):
    return frappe.get_all(
        "Transmittal Drawings",
        filters={"parent": transmittal_name},
        fields=["project_deliverable", "drawing_id", "revision_no", "deliverable_name"]
    )
