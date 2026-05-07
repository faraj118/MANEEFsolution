frappe.ui.form.on("RFI Record", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let billable = frm.doc.is_billable ? "Billable" : "Non-Billable";
        let billableColor = frm.doc.is_billable ? "#10b981" : "#f59e0b";

        let response = frm.doc.status || "Open";
        let responseColor = response === "Responded" ? "#10b981" : response === "Overdue" ? "#ef4444" : "#f59e0b";

        let html = '<div style="padding:12px 0;">';
        html += maneef.sidebar.sidebarItem("Billing Status", billable, billableColor);
        html += maneef.sidebar.sidebarItem("Response Status", response, responseColor);

        if (frm.doc.creation) {
            let days = Math.floor((new Date() - new Date(frm.doc.creation)) / (1000 * 60 * 60 * 24));
            let daysColor = days > 14 ? "#ef4444" : days > 7 ? "#f59e0b" : "#10b981";
            html += maneef.sidebar.sidebarItem("Days Open", days + " days", daysColor);
        }

        html += '</div>';

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
