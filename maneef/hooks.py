app_name = "maneef"
app_title = "Maneef"
app_publisher = "maneef"
app_description = "a tailored maneef solution for engineering companies"
app_email = "info@maneef.ly"
app_license = "mit"

# Apps
# ------------------

# required_apps = []
required_apps = ["erpnext", "hrms"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "maneef",
# 		"logo": "/assets/maneef/logo.png",
# 		"title": "Maneef",
# 		"route": "/maneef",
# 		"has_permission": "maneef.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/maneef/css/maneef.css"
# app_include_js = "/assets/maneef/js/maneef.js"

# include js, css files in header of web template
# web_include_css = "/assets/maneef/css/maneef.css"
# web_include_js = "/assets/maneef/js/maneef.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "maneef/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
    "Company": "public/js/company.js",
    "Project Charter": "public/js/project_charter_sidebar.js",
    "Project": "public/js/project_sidebar.js",
    "Customer": "public/js/customer_sidebar.js",
    "Sales Order": "public/js/sales_order_sidebar.js",
    "RFI Record": "public/js/rfi_sidebar.js",
    "Site Visit Report": "public/js/svr_sidebar.js",
    "Transmittal": "public/js/transmittal_sidebar.js",
    "Risk Assessment": "public/js/risk_assessment_sidebar.js",
    "Task": "public/js/task.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "maneef/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "maneef.utils.jinja_methods",
# 	"filters": "maneef.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "maneef.install.before_install"
after_install = ["maneef.setup.run_post_migrate_setup"]
before_uninstall = "maneef.setup.before_uninstall"
after_migrate = ["maneef.setup.run_post_migrate_setup"]
after_app_install = "maneef.setup.after_app_install"

# Fixtures
# --------
fixtures = [
    "custom_field",
    "property_setter",
    "workflow_state",
    "workflow_action",
    "workflow",
    "print_format",
    "number_card",
    "dashboard_chart",
    "workspace"
]

# Uninstallation
# ------------

# before_uninstall = "maneef.uninstall.before_uninstall"
# after_uninstall = "maneef.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "maneef.utils.before_app_install"
# after_app_install = "maneef.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "maneef.utils.before_app_uninstall"
# after_app_uninstall = "maneef.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "maneef.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Company": {
        "on_update": "maneef.setup.setup_all_companies_coa"
    },
    # ── HRMS Integration ──────────────────────────────────────
    "Employee": {
        "after_insert": "maneef.hr_integration.employee_hooks.after_insert",
        "on_update": "maneef.hr_integration.employee_hooks.on_update",
    },
    "Salary Slip": {
        "on_submit": "maneef.hr_integration.payroll_hooks.on_submit",
    },
    "Leave Application": {
        "on_update": "maneef.hr_integration.leave_hooks.on_update",
    },
    # ─────────────────────────────────────────────────────────
    "Opportunity": {
        "validate": "maneef.crm_commercial.opportunity_hooks.validate",
        "on_update": "maneef.crm_commercial.opportunity_hooks.on_update"
    },
    # Project Charter: on_submit, on_cancel, on_update_after_submit
    # are handled natively by the ProjectCharter controller class
    # in crm_commercial/doctype/project_charter/project_charter.py
    # No doc_events registration needed here.
    "Sales Invoice": {
        "before_submit": "maneef.financial_control.sales_invoice_hooks.before_submit"
    },
    "Payment Entry": {
        "before_submit": "maneef.financial_control.payment_entry_hooks.before_submit"
    },
    "Timesheet": {
        "before_submit": "maneef.financial_control.timesheet_hooks.before_submit",
        "on_submit": "maneef.financial_control.timesheet_hooks.on_submit"
    },
    "Customer": {
        "on_trash": "maneef.crm_commercial.customer_hooks.validate_customer_deletion"
    },
    "Project": {
        "validate": "maneef.design_operations.project_gate_hooks.validate_project_gate_status",
        "on_trash": "maneef.design_operations.project_hooks.validate_project_deletion"
    },
    "Sales Order": {
        "before_submit": "maneef.crm_commercial.sales_order_hooks.before_submit",
        "on_trash": "maneef.crm_commercial.sales_order_hooks.validate_sales_order_deletion"
    }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "maneef.financial_control.timesheet_hooks.daily_burn_rate_update"
    ],
    "hourly": [
        "maneef.financial_control.timesheet_hooks.hourly_burn_alert_check"
    ],
    "weekly": [
        "maneef.construction_control.doctype.rfi_record.rfi_record.weekly_open_items_report"
    ]
}

# Testing
# -------

# before_tests = "maneef.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "maneef.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "maneef.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["maneef.utils.before_request"]
# after_request = ["maneef.utils.after_request"]

# Job Events
# ----------
# before_job = ["maneef.utils.before_job"]
# after_job = ["maneef.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"maneef.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

app_include_js = [
    "/assets/maneef/js/sidebar_utils.js",
    "/assets/maneef/js/project_deliverable.js"
]
