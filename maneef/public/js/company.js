frappe.ui.form.on('Company', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Setup Maneef COA'), function() {
                frappe.confirm(
                    __('This will inject the specialized Maneef AEC Chart of Accounts (Arabic/English) into this company. Existing accounts will not be deleted. Continue?'),
                    function() {
                        frappe.call({
                            method: "maneef.financial_control.chart_of_accounts.coa_builder.setup_maneef_coa",
                            args: {
                                company: frm.doc.name
                            },
                            freeze: true,
                            freeze_message: __("Setting up Chart of Accounts..."),
                            callback: function(r) {
                                if (!r.exc) {
                                    frappe.show_alert({message:__("Chart of Accounts Generatated successfully!"), indicator:'green'});
                                    setTimeout(function() {
                                        frappe.set_route("Tree", "Account");
                                    }, 1500);
                                }
                            }
                        });
                    }
                );
            }, 'Maneef App');
        }
    }
});
