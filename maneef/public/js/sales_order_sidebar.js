frappe.ui.form.on("Sales Order", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let charterStatus = frm.doc.custom_charter_approved ? "Approved" : "Not Approved";
        let charterColor = frm.doc.custom_charter_approved ? "#10b981" : "#f59e0b";

        let html = '<div style="padding:12px 0;">';
        html += maneef.sidebar.sidebarItem("Charter Status", charterStatus, charterColor);

        if (frm.doc.project) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Project",
                    filters: {name: frm.doc.project},
                    fieldname: ["custom_gate_status", "custom_contract_status"]
                },
                callback: function(r) {
                    if (r.message) {
                        let gate = r.message.custom_gate_status || "Not Set";
                        let gateColor = {"Gate 1": "#3b82f6", "Gate 2": "#8b5cf6", "Gate 3": "#06b6d4", "Complete": "#10b981"}[gate] || "#64748b";
                        html += maneef.sidebar.sidebarItem("Project Gate", gate, gateColor);

                        let contract = r.message.custom_contract_status || "Not Set";
                        let contractColor = contract === "Active" ? "#10b981" : contract === "Closed" ? "#64748b" : "#f59e0b";
                        html += maneef.sidebar.sidebarItem("Project Status", contract, contractColor);
                    }

                    html += '</div>';
                    html += _quickLinks(frm);
                    frm.sidebar_area.empty().append(html);
                }
            });
        } else {
            html += '</div>';
            html += _quickLinks(frm);
            frm.sidebar_area.empty().append(html);
        }
    }
});

function _quickLinks(frm) {
    let html = '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
    html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';
    if (frm.doc.custom_project_charter) {
        html += '<div style="margin-bottom:6px;"><a href="/app/project-charter/' + frm.doc.custom_project_charter + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Charter: ' + frm.doc.custom_project_charter + ' &rarr;</a></div>';
    }
    if (frm.doc.project) {
        html += '<div style="margin-bottom:6px;"><a href="/app/project/' + frm.doc.project + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Project: ' + frm.doc.project + ' &rarr;</a></div>';
    }
    html += '</div>';
    return html;
}
