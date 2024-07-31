# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns, data = get_columns(filters), get_data(filters)
	return columns, data

def get_data(filters):
	regional_office = []
	regional_office = frappe.db.sql("""SELECT name FROM `tabRegional Office` where {0}""".format(get_conditions(filters)), as_list=1, debug=1)
	for row in regional_office:
		app_subm = frappe.db.sql("""SELECT regional_office, count(name) as app_subm from `tabJute Mark India Registration form` where workflow_state='Application Submitted' and regional_office='{0}' group by regional_office""".format(row[0]), as_dict=1)
		if app_subm:
			row.append(app_sub[0].get("app_subm"))
		else:
			row.append(0)

		appr_data = frappe.db.sql("""SELECT regional_office, count(name) as app_appr from `tabJute Mark India Registration form` where workflow_state in ('Approved By RO', 'Approved By HO') and regional_office='{0}' group by regional_office""".format(row[0]), as_dict=1)
		if appr_data:
			row.append(appr_data[0].get("app_appr"))
		else:
			row.append(0)

		rej_data = frappe.db.sql("""SELECT regional_office, count(name) as app_rej from `tabJute Mark India Registration form` where workflow_state in ('Rejected by RO', 'Rejected by HO') and regional_office='{0}' group by regional_office""".format(row[0]), as_dict=1)
		if rej_data:
			row.append(rej_data[0].get("rej_data"))
		else:
			row.append(0)

		allocated = frappe.db.sql("""SELECT count(name) as allocated FROM `tabJMI QR Code` where status="Allocated" and allocated_to='{0}' group by allocated_to""".format(row[0]), as_dict=1)
		if allocated:
			row.append(allocated[0].get("allocated"))
		else:
			row.append(0)

	return regional_office


def get_conditions(filters):
	conditions = "1=1"
	if filters.get("regional_office"):
		conditions += " and name = '{0}'".format(filters.get('regional_office'))
	return conditions

def get_columns(filters):
	return[
		_("Regional Office") + ":Link/Regional Office:150",
		_("Application Submitted") + ":Float:150",
		_("Application Approved") + ":Float:150",
		_("Application Rejected") + ":Float:150",
		_("Sold Labels") + ":Float:150"
	]
