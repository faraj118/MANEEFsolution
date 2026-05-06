frappe.ui.form.on("Risk Assessment", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let html = '<div style="padding:12px 0;">';

        // Overall Risk Rating
        let overall = frm.doc.overall_risk_rating || "Not Calculated";
        let overallColor = maneef.sidebar.getRiskColor(overall);
        html += maneef.sidebar.sidebarItem("Overall Risk", overall, overallColor);

        // Overall Score
        if (frm.doc.overall_risk_score !== undefined && frm.doc.overall_risk_score !== null) {
            html += sidebarItem("Risk Score", frm.doc.overall_risk_score + " / 4.0", overallColor);
        }

        // Three Individual Ratings
        html += '</div>';
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Risk Breakdown</div>';

        let payment = frm.doc.payment_risk_rating || "N/A";
        html += sidebarItem("Payment Risk", payment, getRiskColor(payment));

        let commercial = frm.doc.commercial_risk_rating || "N/A";
        html += sidebarItem("Commercial Risk", commercial, getRiskColor(commercial));

        let duration = frm.doc.duration_risk_rating || "N/A";
        html += sidebarItem("Duration Risk", duration, getRiskColor(duration));

        html += '</div>';

        // Linked Record Data
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Linked Data</div>';

        if (frm.doc.customer_project_count !== undefined) {
            html += sidebarItem("Customer Projects", frm.doc.customer_project_count, "#e2e8f0");
        }

        if (frm.doc.customer_overdue_invoices !== undefined) {
            let overdueColor = frm.doc.customer_overdue_invoices > 0 ? "#ef4444" : "#10b981";
            html += sidebarItem("Overdue Invoices", frm.doc.customer_overdue_invoices, overdueColor);
        }

        if (frm.doc.project_burn_percentage !== undefined && frm.doc.project_burn_percentage !== null) {
            let burn = frm.doc.project_burn_percentage;
            let burnColor = burn >= 100 ? "#ef4444" : burn >= 80 ? "#f59e0b" : "#10b981";
            html += sidebarItem("Burn Rate", burn + "%", burnColor);
        }

        if (frm.doc.project_open_rfis !== undefined) {
            let rfiColor = frm.doc.project_open_rfis > 5 ? "#ef4444" : frm.doc.project_open_rfis > 0 ? "#f59e0b" : "#10b981";
            html += sidebarItem("Open RFIs", frm.doc.project_open_rfis, rfiColor);
        }

        if (frm.doc.project_open_snags !== undefined) {
            let snagColor = frm.doc.project_open_snags > 3 ? "#ef4444" : frm.doc.project_open_snags > 0 ? "#f59e0b" : "#10b981";
            html += sidebarItem("Open Snags", frm.doc.project_open_snags, snagColor);
        }

        html += '</div>';

        // Quick Links
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';

        if (frm.doc.project_charter) {
            html += '<div style="margin-bottom:6px;"><a href="/app/project-charter/' + frm.doc.project_charter + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Charter: ' + frm.doc.project_charter + ' &rarr;</a></div>';
        }
        if (frm.doc.project) {
            html += '<div style="margin-bottom:6px;"><a href="/app/project/' + frm.doc.project + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Project: ' + frm.doc.project + ' &rarr;</a></div>';
        }
        if (frm.doc.customer) {
            html += '<div style="margin-bottom:6px;"><a href="/app/customer/' + frm.doc.customer + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Customer: ' + frm.doc.customer + ' &rarr;</a></div>';
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

function getRiskColor(rating) {
    let colors = {
        "Low": "#10b981", "Green": "#10b981",
        "Medium": "#f59e0b", "Amber": "#f59e0b",
        "High": "#ef4444", "Red": "#ef4444",
        "Unacceptable": "#ef4444", "Critical": "#ef4444"
    };
    return colors[rating] || "#64748b";
}
