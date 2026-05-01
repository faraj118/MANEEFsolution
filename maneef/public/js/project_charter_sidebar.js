frappe.ui.form.on("Project Charter", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let html = '<div style="padding:12px 0;">';

        // GO/NO-GO Status
        let goStatus = frm.doc.go_no_go_decision || "Not Set";
        let goColor = goStatus === "GO" ? "#10b981" : goStatus === "NO-GO" ? "#ef4444" : "#64748b";
        html += sidebarItem("GO/NO-GO Decision", goStatus, goColor);

        // Contract Status
        let contractStatus = frm.doc.custom_contract_status || "Not Set";
        let contractColor = contractStatus === "Signed" ? "#10b981" : "#f59e0b";
        html += sidebarItem("Contract Status", contractStatus, contractColor);

        // Payment Risk
        let paymentRisk = frm.doc.custom_payment_risk_rating || "Not Assessed";
        html += sidebarItem("Payment Risk", paymentRisk, getRiskColor(paymentRisk));

        // Commercial Risk
        let commercialRisk = frm.doc.custom_commercial_risk_rating || "Not Assessed";
        html += sidebarItem("Commercial Risk", commercialRisk, getRiskColor(commercialRisk));

        // Duration Risk
        let durationRisk = frm.doc.custom_duration_risk_rating || "Not Assessed";
        html += sidebarItem("Duration Risk", durationRisk, getRiskColor(durationRisk));

        // Projected Margin
        if (frm.doc.custom_projected_margin !== undefined && frm.doc.custom_projected_margin !== null) {
            let margin = frm.doc.custom_projected_margin;
            let marginColor = margin >= 20 ? "#10b981" : margin >= 10 ? "#f59e0b" : "#ef4444";
            html += sidebarItem("Projected Margin", margin + "%", marginColor);
        }

        html += '</div>';

        // Risk Assessment Section
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Risk Assessment</div>';

        // Linked Risk Assessment
        if (frm.doc.linked_risk_assessment) {
            html += '<div style="margin-bottom:6px;"><a href="/app/risk-assessment/' + frm.doc.linked_risk_assessment + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">View Risk Assessment &rarr;</a></div>';
        }

        // Create Risk Assessment Button
        if (!frm.doc.linked_risk_assessment) {
            html += '<div style="margin-bottom:6px;"><button class="btn btn-xs btn-default" style="font-size:11px;padding:4px 8px;background:#1e293b;color:#e2e8f0;border:1px solid #334155;border-radius:4px;cursor:pointer;" onclick="createRiskAssessment(\'' + frm.doc.name + '\')">Create Risk Assessment</button></div>';
        }

        html += '</div>';

        // Quick Links
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';

        if (frm.doc.sales_order) {
            html += '<div style="margin-bottom:6px;"><a href="/app/sales-order/' + frm.doc.sales_order + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Sales Order: ' + frm.doc.sales_order + ' &rarr;</a></div>';
        }

        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Project\', {\'custom_project_charter\': \'' + frm.doc.name + '\'});return false;">Linked Projects &rarr;</a></div>';
        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Task\', {\'custom_project_charter\': \'' + frm.doc.name + '\'});return false;">Tasks &rarr;</a></div>';
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

function createRiskAssessment(charter_name) {
    cur_frm.call({
        method: "create_risk_assessment",
        callback: function(r) {
            cur_frm.reload_doc();
        }
    });
}
