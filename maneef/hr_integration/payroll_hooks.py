"""
Maneef HR Integration — Payroll & Salary hooks.

On Salary Slip submission: distribute the employee's payroll cost
to their active project cost centers using the Timesheet hours ratio.
This feeds the burn-rate engine in financial_control/timesheet_hooks.py.
"""

import frappe
from frappe import _
from frappe.utils import flt


def on_submit(doc, method=None):
    """Distribute salary cost to projects on Salary Slip submission."""
    _allocate_salary_to_projects(doc)


def _allocate_salary_to_projects(salary_slip):
    employee = salary_slip.employee
    month_start = salary_slip.start_date
    month_end = salary_slip.end_date
    gross = flt(salary_slip.gross_pay)

    if not gross:
        return

    # Get submitted timesheet hours per project for this employee in the period
    rows = frappe.db.sql(
        """
        SELECT td.project, SUM(td.hours) AS total_hours
        FROM `tabTimesheet Detail` td
        JOIN `tabTimesheet` ts ON td.parent = ts.name
        WHERE ts.employee = %s
          AND ts.docstatus = 1
          AND td.from_time BETWEEN %s AND %s
          AND td.project IS NOT NULL
          AND td.project != ''
        GROUP BY td.project
        """,
        (employee, month_start, month_end),
        as_dict=True,
    )

    if not rows:
        return

    total_hours = sum(r.total_hours for r in rows)
    if not total_hours:
        return

    for row in rows:
        ratio = flt(row.total_hours) / total_hours
        allocated_cost = flt(gross * ratio, 2)
        _update_project_salary_cost(row.project, allocated_cost, salary_slip.name)


def _update_project_salary_cost(project_name, cost, salary_slip_name):
    """Add the salary cost to the project's custom_actual_cost_to_date."""
    if not frappe.db.exists("Project", project_name):
        return

    current = flt(frappe.db.get_value("Project", project_name, "custom_actual_cost_to_date"))
    frappe.db.set_value("Project", project_name, "custom_actual_cost_to_date", current + cost)

    # Re-run burn rate after salary injection
    from maneef.financial_control.timesheet_hooks import _update_project_burn
    try:
        _update_project_burn(project_name)
    except Exception as e:
        frappe.log_error(str(e), "Salary-to-Project Burn Rate Error")

    frappe.logger().info(
        "Allocated salary cost %.2f from %s to Project %s", cost, salary_slip_name, project_name
    )
