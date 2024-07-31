// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Label Fulfilment Report"] = {
	"filters": [

		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 0,
			
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 0,
			
		},

	]
};
