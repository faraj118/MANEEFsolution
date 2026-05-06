frappe.ui.form.on("Project Charter", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let html = '<div style="padding:12px 0;">';

        // GO/NO-GO Status
        let goStatus = frm.doc.go_no_go_decision || "Not Set";
        let goColor = goStatus === "GO" ? "#10b981" : goStatus === "NO-GO" ? "#ef4444" : "#64748b";
        html += maneef.sidebar.sidebarItem("GO/NO-GO Decision", goStatus, goColor);

        // Contract Status
        let contractStatus = frm.doc.custom_contract_status || "Not Set";
        let contractColor = contractStatus === "Signed" ? "#10b981" : "#f59e0b";
        html += maneef.sidebar.sidebarItem("Contract Status", contractStatus, contractColor);

        // Payment Risk
        let paymentRisk = frm.doc.custom_payment_risk_rating || "Not Assessed";
        html += maneef.sidebar.sidebarItem("Payment Risk", paymentRisk, maneef.sidebar.getRiskColor(paymentRisk));

        // Commercial Risk
        let commercialRisk = frm.doc.custom_commercial_risk_rating || "Not Assessed";
        html += maneef.sidebar.sidebarItem("Commercial Risk", commercialRisk, maneef.sidebar.getRiskColor(commercialRisk));

        // Duration Risk
        let durationRisk = frm.doc.custom_duration_risk_rating || "Not Assessed";
        html += maneef.sidebar.sidebarItem("Duration Risk", durationRisk, maneef.sidebar.getRiskColor(durationRisk));

        // Projected Margin
        if (frm.doc.custom_projected_margin !== undefined && frm.doc.custom_projected_margin !== null) {
            let margin = frm.doc.custom_projected_margin;
            let marginColor = margin >= 20 ? "#10b981" : margin >= 10 ? "#f59e0b" : "#ef4444";
            html += maneef.sidebar.sidebarItem("Projected Margin", margin + "%", marginColor);
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
