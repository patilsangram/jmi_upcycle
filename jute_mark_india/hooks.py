from . import __version__ as app_version

app_name = "jute_mark_india"
app_title = "jute_mark_india"
app_publisher = "admin"
app_description = "jute_mark_india"
app_email = "admin@example.com"
app_license = "MIT"
app_logo_url = "/assets/jute_mark_india/images/JuteMark-logo.jpg"
# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/jute_mark_india/css/jute_mark_india.css"
app_include_js = ["/assets/jute_mark_india/js/desk.js", "/assets/jute_mark_india/js/field_validator.js"]

# include js, css files in header of web template
# web_include_css = "/assets/jute_mark_india/css/jute_mark_india.css"
# web_include_js = "/assets/jute_mark_india/js/jute_mark_india.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "jute_mark_india/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_list_js = {"Request for Label" : "jute_mark_india/jute_mark_india/doctype/request_for_label/request_for_label/request_for_label_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "/app/jute-mark-india"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "jute_mark_india.utils.jinja_methods",
#	"filters": "jute_mark_india.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "jute_mark_india.install.before_install"
# after_install = "jute_mark_india.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "jute_mark_india.uninstall.before_uninstall"
# after_uninstall = "jute_mark_india.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "jute_mark_india.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
permission_query_conditions = {
	"Jute Mark India Registration form": "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.get_permission_query_conditions",
	"JMI QR Code" : "jute_mark_india.jute_mark_india.doctype.jmi_qr_code.jmi_qr_code.get_permission_query_conditions_jmi_qr",
	"Roll wise QR" : "jute_mark_india.jute_mark_india.doctype.roll_wise_qr.roll_wise_qr.get_permission_query_conditions_roll",
	"Request for Label" : "jute_mark_india.jute_mark_india.doctype.request_for_label.request_for_label.get_permission_query_conditions_request_label",
	"JMI Appeal" : "jute_mark_india.jute_mark_india.doctype.jmi_appeal.jmi_appeal.get_permission_query_conditions",
	"Label Enhancement" : "jute_mark_india.jute_mark_india.doctype.label_enhancement.label_enhancement.get_permission_query_conditions",
	"Application Renewal" : "jute_mark_india.jute_mark_india.doctype.application_renewal.application_renewal.get_permission_query_conditions",
	"Actual Site Visit Plan" : "jute_mark_india.jute_mark_india.doctype.actual_site_visit_plan.actual_site_visit_plan.get_permission_query_conditions_visit"
}
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
	# "Jute Mark India Registration form": {
		# "before_save": "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form/jute_mark_india_registration_form.py",
		# "on_cancel": "method",
		# "on_trash": "method"
# 	}
# }

write_file = "jute_mark_india.jute_mark_india.docevents.file.save_file_on_filesystem"
doc_events = {
	'Notification Log': {
		'after_insert': 'jute_mark_india.jute_mark_india.docevents.notification_log.send_push_notification'
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"jute_mark_india.jute_mark_india.utils.user_registration_hourly_scheduler"
	],
	"daily": [
		"jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.jmi_application_renew"
	]
}

# scheduler_events = {
#	"all": [
#		"jute_mark_india.tasks.all"
#	],
#	"daily": [
#		"jute_mark_india.tasks.daily"
#	],
#	"hourly": [
#		"jute_mark_india.tasks.hourly"
#	],
#	"weekly": [
#		"jute_mark_india.tasks.weekly"
#	],
#	"monthly": [
#		"jute_mark_india.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "jute_mark_india.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "jute_mark_india.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "jute_mark_india.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


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
website_context = {
	"favicon": "/assets/jute_mark_india/images/JuteMark-logo.jpg",
	"splash_image": "/assets/jute_mark_india/images/JuteMark-logo.jpg",
}

signup_form_template = "/templates/signup-form.html"

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"jute_mark_india.auth.validate"
# ]
#calendars = ["Actual Site Visit Plan"]
fixtures = ["Workflow","Workflow State","Workflow Action Master","Website Theme", "Web Page","Client Script", "Website Settings"]
