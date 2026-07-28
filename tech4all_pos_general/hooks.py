from . import __version__ as app_version

app_name = "tech4all_pos_general"
app_title = "Tech4all POS General"
app_publisher = "tech4allERP"
app_description = "Tech4all POS General"
app_email = "info@tech4allerp.cojm"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tech4all_pos_general/css/tech4all_pos_general.css"
# app_include_js = "/assets/tech4all_pos_general/js/tech4all_pos_general.js"

# include js, css files in header of web template
# web_include_css = "/assets/tech4all_pos_general/css/tech4all_pos_general.css"
# web_include_js = "/assets/tech4all_pos_general/js/tech4all_pos_general.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tech4all_pos_general/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Sales Order": "public/js/sales_order_custom.js",
    "Customer": ["public/js/customer_custom.js", "public/js/general_activities.js"],
    "POS Profile": "public/js/pos_payment_method_custom.js",
    "Data Import": "public/js/data_import_custom.js",
    "Payment Entry": "public/js/payment_entry_cheque.js",
    "Journal Entry": "public/js/journal_entry_cheque.js",
    "User": "public/js/user_custom.js",
    "Role Profile": "public/js/role_profile_custom.js",
    "Document Naming Rule": "public/js/document_naming_rule.js",
    "Customize Form": "public/js/customize_form_custom.js",
    "Department": "public/js/department_general.js",
}

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------
# auth_hooks = ["tech4all_pos_general.custom.utils.validate_user_ip"]
# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }
app_include_js = [
    "/assets/tech4all_pos_general/js/global_realtime_listener.js",
    "tech4all_general.bundle.js",
    "document_defaults.bundle.js",
]

extend_bootinfo = "tech4all_pos_general.general_boot.boot_session"

jinja = {
    "methods": "tech4all_pos_general.general_utils.get_itemised_tax"
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "tech4all_pos_general.utils.jinja_methods",
#	"filters": "tech4all_pos_general.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tech4all_pos_general.install.before_install"
# after_install = "tech4all_pos_general.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tech4all_pos_general.uninstall.before_uninstall"
# after_uninstall = "tech4all_pos_general.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tech4all_pos_general.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Document Naming Rule":
        "tech4all_pos_general.general_overrides.document_naming_rule_override.DocumentNamingRuleOverride",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "*": {
        "before_naming": "tech4all_pos_general.general_utils.before_naming",
        "validate": "tech4all_pos_general.custom.general_cost_center_custom.cost_center_validation",
    },
    "Sales Order": {
        "validate": "tech4all_pos_general.custom.sales_order_custom.validate",
        "after_insert": "tech4all_pos_general.custom.sales_order_custom.after_insert",
        "on_submit": "tech4all_pos_general.custom.sales_order_custom.on_submit",
      
    },
    "Sales Invoice": {
        "before_save": "tech4all_pos_general.custom.sales_invoice_custom.before_save_invoice",
        "on_submit": [
            "tech4all_pos_general.custom.sales_invoice_custom.on_submit",
            "tech4all_pos_general.custom.sales_invoice_custom.before_save_invoice",
            "tech4all_pos_general.custom.general_sales_invoice_custom.post_commission_jv",
        ],
        "on_update": "tech4all_pos_general.custom.sales_invoice_custom.on_update",
        "on_cancel": "tech4all_pos_general.custom.sales_invoice_custom.on_cancel"
    },
    "Payment Entry": {
        "before_submit": "tech4all_pos_general.custom.general_payment_entry_custom.before_submit",
        "on_cancel": "tech4all_pos_general.custom.general_payment_entry_custom.on_cancel",
    },
    "Journal Entry": {
        "validate": "tech4all_pos_general.custom.general_journal_entry_custom.on_validate",
        "on_submit": "tech4all_pos_general.custom.general_journal_entry_custom.on_submit",
        "on_cancel": "tech4all_pos_general.custom.general_journal_entry_custom.on_cancel",
    },
    ("Custom Field", "Property Setter"): {
        "before_insert": "tech4all_pos_general.custom.general_customize_form_custom.before_insert",
        "validate": "tech4all_pos_general.custom.general_customize_form_custom.before_insert",
    },
    "User": {
        "onload": "tech4all_pos_general.general_utils.onload_user",
    },
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"tech4all_pos_general.tasks.all"
#	],
#	"daily": [
#		"tech4all_pos_general.tasks.daily"
#	],
#	"hourly": [
#		"tech4all_pos_general.tasks.hourly"
#	],
#	"weekly": [
#		"tech4all_pos_general.tasks.weekly"
#	],
#	"monthly": [
#		"tech4all_pos_general.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "tech4all_pos_general.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
    "frappe.desk.reportview.get":
        "tech4all_pos_general.api.view_override.custom_get_list",
    "tech4all.accounts.doctype.payment_entry.payment_entry.get_outstanding_reference_documents":
        "tech4all_pos_general.custom.general_payment_entry_custom.get_outstanding_reference_documents_override",
    "frappe.core.doctype.user.user.get_all_roles":
        "tech4all_pos_general.general_utils.get_all_roles",
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Ducky apps
# override_doctype_dashboards = {
#	"Task": "tech4all_pos_general.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tech4all_pos_general.utils.before_request"]
# after_request = ["tech4all_pos_general.utils.after_request"]

# Job Events
# ----------
# before_job = ["tech4all_pos_general.utils.before_job"]
# after_job = ["tech4all_pos_general.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"tech4all_pos_general.auth.validate"
# ]
