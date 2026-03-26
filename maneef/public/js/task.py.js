frappe.ui.form.on('Task', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            if (frm.doc.custom_check_in_status === 'Checked Out') {
                frm.add_custom_button(__('Check In'), function() {
                    frappe.call({
                        method: 'maneef.design_operations.api.task_check_in',
                        args: {
                            task_name: frm.doc.name
                        },
                        callback: function(r) {
                            if (r.message) {
                                frm.reload_doc();
                                frappe.show_alert({message: __('Checked in to task'), indicator: 'green'});
                            }
                        }
                    });
                }).addClass('btn-primary');
            } else {
                frm.add_custom_button(__('Check Out'), function() {
                    frappe.call({
                        method: 'maneef.design_operations.api.task_check_out',
                        args: {
                            task_name: frm.doc.name
                        },
                        callback: function(r) {
                            if (r.message) {
                                frm.reload_doc();
                                frappe.show_alert({message: __('Checked out of task'), indicator: 'red'});
                            }
                        }
                    });
                }).addClass('btn-danger');
            }
        }
    }
});
