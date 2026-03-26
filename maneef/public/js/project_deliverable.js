// NOTE: This is UI-only protection.
// Server-side enforcement is in project_deliverable.py _enforce_ip_lock()

frappe.ui.form.on('Project Deliverable', {
    refresh: function(frm) {
        if (frm.doc.status === 'Approved' && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create New Revision'), function() {
                frm.call('create_new_revision').then(r => {
                    if(!r.exc) frm.reload_doc();
                });
            }).addClass('btn-primary');
        }
        if (!frm.doc.project) return;
        frappe.db.get_value('Sales Order', {project: frm.doc.project, docstatus: 1}, 'custom_contract_status')
            .then(r => {
                const status = r.message && r.message.custom_contract_status;
                if (["Signed", "Active"].includes(status)) {
                    frm.enable_save();
                    frm.set_intro("");
                } else {
                    frm.disable_save();
                    frm.set_intro(__("IP Protection Lock: No signed contract for this project. Deliverables cannot be created or edited."), "red");
                }
            });
    }
});