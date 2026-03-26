frappe.query_reports["Project Health Matrix"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("Project Status"),
            "fieldtype": "Select",
            "options": "\nOpen\nCompleted\nCancelled",
            "default": "Open"
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname == "burn_pct" && data.burn_pct >= 80) {
            value = "<span style='color:red; font-weight:bold'>" + value + "</span>";
        }
        else if (column.fieldname == "burn_pct" && data.burn_pct >= 50) {
            value = "<span style='color:orange; font-weight:bold'>" + value + "</span>";
        }
        return value;
    }
};
