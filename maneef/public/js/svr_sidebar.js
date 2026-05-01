frappe.ui.form.on("Site Visit Report", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        frappe.call({
            method: "frappe.client.get_count",
            args: {
                doctype: "SVR Photo",
                filters: {site_visit_report: frm.doc.name}
            },
            callback: function(r) {
                let photos = r.message || 0;

                frappe.call({
                    method: "frappe.client.get_count",
                    args: {
                        doctype: "SVR Issue",
                        filters: {site_visit_report: frm.doc.name, status: ["!=", "Closed"]}
                    },
                    callback: function(r2) {
                        let openIssues = r2.message || 0;

                        let html = '<div style="padding:12px 0;">';
                        html += sidebarItem("Photos Attached", photos, photos > 0 ? "#10b981" : "#f59e0b");
                        html += sidebarItem("Open Issues", openIssues, openIssues > 0 ? "#ef4444" : "#10b981");
                        html += '</div>';

                        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
                        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';

                        if (frm.doc.project) {
                            html += '<div style="margin-bottom:6px;"><a href="/app/project/' + frm.doc.project + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Project: ' + frm.doc.project + ' &rarr;</a></div>';
                        }

                        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'SVR Issue\', {\'site_visit_report\': \'' + frm.doc.name + '\'});return false;">Issues &rarr;</a></div>';
                        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'SVR Photo\', {\'site_visit_report\': \'' + frm.doc.name + '\'});return false;">Photos &rarr;</a></div>';

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
