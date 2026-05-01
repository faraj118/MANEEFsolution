frappe.ui.form.on("Transmittal", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let html = '<div style="padding:12px 0;">';

        // Submission Status
        let submitted = frm.doc.docstatus === 1;
        let statusText = submitted ? "Issued (Immutable)" : "Draft";
        let statusColor = submitted ? "#10b981" : "#f59e0b";
        html += sidebarItem("Status", statusText, statusColor);

        // Drawings count from child table
        let drawingsCount = (frm.doc.drawings || []).length;
        html += sidebarItem("Drawings Included", drawingsCount, drawingsCount > 0 ? "#e2e8f0" : "#f59e0b");

        html += '</div>';

        // Quick Links
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';

        if (frm.doc.project) {
            html += '<div style="margin-bottom:6px;"><a href="/app/project/' + frm.doc.project + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Project: ' + frm.doc.project + ' &rarr;</a></div>';
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
