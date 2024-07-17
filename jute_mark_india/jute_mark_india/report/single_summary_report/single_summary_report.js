// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Single Summary Report"] = {
	"filters": [
		{
			"fieldname": "regional_office",
			"label": __("Regional Office"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Regional Office",
			"reqd": 0,
		}
	]
};

