// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Label Stock Report"] = {
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
		{
			"fieldname":"from_qr_code",
			"label": __("From QR Code"),
			"fieldtype": "Data",
			"width": "80",
			"reqd": 0,
			
		},
		{
			"fieldname":"to_qr_code",
			"label": __("To QR Code"),
			"fieldtype": "Data",
			"width": "80",
			"reqd": 0,
			
		},
		{
			"fieldname": "district",
			"label": __("Regional Office"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Regional Office",
			"reqd": 0,
			"default": frappe.defaults.get_default("Regional Office")
		},
		// {
		// 	"fieldname": "application_no",
		// 	"label": __("Application No"),
		// 	"fieldtype": "Link",
		// 	"width": "100",
		// 	"options": "On-Site Verification Form",
		// 	"reqd": 0,
			
		// },
		// {
		// 	"fieldname": "total_no_of_labels",
		// 	"label": __("Total no. of Labels"),
		// 	"fieldtype": "Data",
		// 	"width": "80",
		// 	"reqd": 0,
			
		// },
	]
};
