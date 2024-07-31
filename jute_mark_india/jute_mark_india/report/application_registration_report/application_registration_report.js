// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Application registration Report"] = {
	"filters": [
		{
			"fieldname": "district",
			"label": __("Regional Office"),
			"fieldtype": "Link",
			"width": "100",
			"options": "Regional Office",
			"reqd": 0,
			"default": frappe.defaults.get_default("Regional Office")
		},
		{
			"fieldname":"category_b",
			"label": __("Category"),
			"fieldtype": "Select",
			"options":"\nArtisan\nManufacturer\nRetailer",
			"width": "80",
			"reqd": 0,
			
		},
		{
			"fieldname":"gender",
			"label": __("Gender"),
			"fieldtype": "Select",
			"options":"\nMale\nFemale\nOther",
			"width": "80",
			"reqd": 0,
			
		},
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
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options":"\nApproval Pending By RO\nApproval Pending By HO\nApproved By HO\nApproved By RO\nRejected by HO",
			"width": "80",
			"reqd": 0,
			
		},
		// {
		// 	"fieldname": "status",
		// 	"label": __("Status"),
		// 	"fieldtype": "Select",
		// 	"width": "80",
		// 	"options" = ['Submitted', 'Approval Pending By RO','Approval Pending By HO', 'Approved By HO', 'Approved By RO','Rejected by HO']
		// 	"width": "80",
		// 	"reqd": 0,	
			
		// },
	]
};
