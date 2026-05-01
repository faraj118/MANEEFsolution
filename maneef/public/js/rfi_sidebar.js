frappe.ui.form.on("RFI Record", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let html = '<div style="padding:12px 0;">';

        // Billable Status
        let billable = frm.doc.is_billable ? "Billable" : "Non-Billable";
        let billableColor = frm.doc.is_billable ? "#10b981" : "#f59e0b";
        html += sidebarItem("Billing Status", billable, billableColor);

        // Response Status
        let response = frm.doc.status || "Open";
        let responseColor = response === "Responded" ? "#10b981" : response === "Overdue" ? "#ef4444" : "#f59e0b";
        html += sidebarItem("Response Status", response, responseColor);

        // Days Open
        if (frm.doc.creation) {
            let created = new Date(frm.doc.creation);
            let now = new Date();
            let days = Math.floor((now - created) / (1000 * 60 * 60 * 24));
            let daysColor = days > 14 ? "#ef4444" : days > 7 ? "#f59e0b" : "#10b981";
            html += sidebarItem("Days Open", days + " days", daysColor);
        }

        html += '</div>';

        // Quick Links
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';

        if (frm.doc.project) {
            html += '<div style="margin-bottom:6px;"><a href="/app/project/' + frm.doc.project + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Project: ' + frm.doc.project + ' &rarr;</a></div>';
        }
        if (frm.doc.custom_site_visit_report) {
            html += '<div style="margin-bottom:6px;"><a href="/app/site-visit-report/' + frm.doc.custom_site_visit_report + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Site Visit Report &rarr;</a></div>';
        }

        html += '</div>';

        frm.sidebar_area.empty().append(html);
    }
});

function sidebarItem(label, value, color) {
    return '<div style="margin-bottom:10px;">' +
        '<div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:2px;">' + label + '</div>' +
        '<div style="font-size:13px;font-weight:600;color:' + color + ';">' + value + '</div>' +
        '</div>';
}
