frappe.ui.form.on("Project", {
    refresh: function(frm) {
        if (frm.doc.__islocal) return;

        let html = '<div style="padding:12px 0;">';

        // Gate Status
        let gate = frm.doc.custom_gate_status || "Not Set";
        let gateColor = {"Gate 1": "#3b82f6", "Gate 2": "#8b5cf6", "Gate 3": "#06b6d4", "Complete": "#10b981"}[gate] || "#64748b";
        html += maneef.sidebar.sidebarItem("Current Gate", gate, gateColor);

        // Contract Status
        let contract = frm.doc.custom_contract_status || "Not Set";
        let contractColor = contract === "Active" ? "#10b981" : contract === "Closed" ? "#64748b" : "#f59e0b";
        html += maneef.sidebar.sidebarItem("Contract Status", contract, contractColor);

        // Burn Percentage
        if (frm.doc.custom_burn_percentage !== undefined && frm.doc.custom_burn_percentage !== null) {
            let burn = frm.doc.custom_burn_percentage;
            let burnColor = burn >= 100 ? "#ef4444" : burn >= 80 ? "#f59e0b" : "#10b981";
            html += maneef.sidebar.sidebarItem("Burn Rate", burn + "%", burnColor);
        }

        // Contracted Fee
        if (frm.doc.custom_contracted_fee) {
            html += maneef.sidebar.sidebarItem("Contracted Fee", maneef.sidebar.formatCurrency(frm.doc.custom_contracted_fee), "#e2e8f0");
        }

        html += '</div>';

        // Risk Summary placeholder
        html += '<div id="risk_profile_area"></div>';

        // Quick Links
        html += '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
        html += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Quick Links</div>';

        if (frm.doc.custom_project_charter) {
            html += '<div style="margin-bottom:6px;"><a href="/app/project-charter/' + frm.doc.custom_project_charter + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Charter: ' + frm.doc.custom_project_charter + ' &rarr;</a></div>';
        }
        if (frm.doc.sales_order) {
            html += '<div style="margin-bottom:6px;"><a href="/app/sales-order/' + frm.doc.sales_order + '" style="font-size:12px;color:#60a5fa;text-decoration:none;">Sales Order: ' + frm.doc.sales_order + ' &rarr;</a></div>';
        }

        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Project BOQ\', {\'project\': \'' + frm.doc.name + '\'});return false;">BOQs &rarr;</a></div>';
        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Site Visit Report\', {\'project\': \'' + frm.doc.name + '\'});return false;">Site Visit Reports &rarr;</a></div>';
        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'RFI Record\', {\'project\': \'' + frm.doc.name + '\'});return false;">RFIs &rarr;</a></div>';
        html += '<div style="margin-bottom:6px;"><a href="#" style="font-size:12px;color:#60a5fa;text-decoration:none;" onclick="frappe.set_route(\'List\', \'Task\', {\'project\': \'' + frm.doc.name + '\'});return false;">Tasks &rarr;</a></div>';

        html += '</div>';

        frm.sidebar_area.empty().append(html);

        if (frm.doc.custom_project_charter) {
            frappe.db.get_value("Project Charter", frm.doc.custom_project_charter, 
                ["custom_payment_risk_rating", "custom_commercial_risk_rating", "custom_duration_risk_rating"])
            .then(r => {
                if (r && r.message) {
                    let riskHtml = '<div style="padding:8px 0;border-top:1px solid #1e293b;margin-top:8px;">';
                    riskHtml += '<div style="font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;">Risk Profile</div>';
                    
                    let paymentRisk = r.message.custom_payment_risk_rating || "N/A";
                    riskHtml += maneef.sidebar.sidebarItem("Payment Risk", paymentRisk, maneef.sidebar.getRiskColor(paymentRisk));

                    let commercialRisk = r.message.custom_commercial_risk_rating || "N/A";
                    riskHtml += maneef.sidebar.sidebarItem("Commercial Risk", commercialRisk, maneef.sidebar.getRiskColor(commercialRisk));

                    let durationRisk = r.message.custom_duration_risk_rating || "N/A";
                    riskHtml += maneef.sidebar.sidebarItem("Duration Risk", durationRisk, maneef.sidebar.getRiskColor(durationRisk));

                    riskHtml += '</div>';
                    frm.sidebar_area.find('#risk_profile_area').html(riskHtml);
                }
            });
        }
    }
});
