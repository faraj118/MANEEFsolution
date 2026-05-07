frappe.ui.form.on("Transmittal", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let submitted = frm.doc.docstatus === 1;
        let statusText = submitted ? "Issued (Immutable)" : "Draft";
        let statusColor = submitted ? "#10b981" : "#f59e0b";

        let drawingsCount = (frm.doc.drawings || []).length;

        let html = '<div style="padding:12px 0;">';
        html += maneef.sidebar.sidebarItem("Status", statusText, statusColor);
        html += maneef.sidebar.sidebarItem("Drawings Included", drawingsCount, drawingsCount > 0 ? "#e2e8f0" : "#f59e0b");
        html += '</div>';

        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';

        if (frm.doc.project) {
            html += '<div style="margin-bottom:6px;"><a href="/app/project/' + frm.doc.project + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Project: ' + frm.doc.project + ' &rarr;</a></div>';
        }

        html += '</div>';

        frm.sidebar_area.empty().append(html);
    }
});
