frappe.query_reports["GM Pending Approvals"] = {
    "filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        },
        {
            "fieldname": "deliverable_type",
            "label": __("Deliverable Type"),
            "fieldtype": "Select",
            "options": "\nSD Sketch\nSD Drawing\nDD Drawing\nCD Drawing\nBOQ\nSpecification\nBIM Model\nReport\nPresentation\nOther"
        },
        {
            "fieldname": "overdue_only",
            "label": __("Overdue Only"),
            "fieldtype": "Check",
            "default": 0
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname === "days_overdue" && data && data.days_overdue > 0) {
            value = "<span style='color:red;font-weight:bold;'>" + data.days_overdue + "</span>";
        }
        if (column.fieldname === "due_date" && data && data.days_overdue > 0) {
            value = "<span style='color:red;'>" + value + "</span>";
        }
        return value;
    },
    "onload": function(report) {
        report.page.add_inner_button(__("Approve Selected"), function() {
            let rows = report.get_checked_items();
            if (!rows.length) {
                frappe.msgprint(__("Select at least one deliverable to approve."));
                return;
            }
            frappe.confirm(
                __("Approve {0} deliverable(s)?", [rows.length]),
                function() {
                    let promises = rows.map(r =>
                        frappe.db.set_value("Project Deliverable", r.name, "principal_approved", 1)
                    );
                    Promise.all(promises).then(() => {
                        frappe.show_alert({ message: __("Approvals saved"), indicator: "green" });
                        report.refresh();
                    });
                }
            );
        });
    }
};
