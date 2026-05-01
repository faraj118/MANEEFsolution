frappe.ui.form.on("Customer", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "Project",
                filters: {customer: frm.doc.name, status: ["in", ["Open", "Work in Progress"]]}
            },
            callback: function(r) {
                let activeProjects = r.message || 0;

                frappe.call({
                    method: "frappe.client.get_count",
                    args: {
                        doctype: "Project Charter",
                        filters: {customer: frm.doc.name, docstatus: 0}
                    },
                    callback: function(r2) {
                        let openCharters = r2.message || 0;

                        let html = '<div style="padding:12px 0;">';
                        html += sidebarItem("Active Projects", activeProjects, activeProjects > 0 ? "#10b981" : "#64748b");
                        html += sidebarItem("Open Charters", openCharters, openCharters > 0 ? "#f59e0b" : "#64748b");
                        html += '</div>';

                        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
                        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';
                        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Project\', {\'customer\': \'' + frm.doc.name + '\'});return false;">All Projects &rarr;</a></div>';
                        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Project Charter\', {\'customer\': \'' + frm.doc.name + '\'});return false;">Project Charters &rarr;</a></div>';
                        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Sales Order\', {\'customer_name\': \'' + frm.doc.customer_name + '\'});return false;">Sales Orders &rarr;</a></div>';
                        html += '</div>';

                        frm.sidebar_area.empty().append(html);
                    }
                });
            }
        });
    }
});

function sidebarItem(label, value, color) {
    return '<div style="margin-bottom:10px;">' +
        '<div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:2px;">' + label + '</div>' +
        '<div style="font-size:13px;font-weight:600;color:' + color + ';">' + value + '</div>' +
        '</div>';
}
