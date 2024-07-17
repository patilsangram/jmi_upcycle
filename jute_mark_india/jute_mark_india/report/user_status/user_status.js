// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["User Status"] = {
	"filters": [

		{
			"fieldname":"status",
			"label": __("Status"),
			"fieldtype": "Select",
			"options":"\nActive\nInactive",
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
		{
			"fieldname":"religion",
			"label": __("Religion"),
			"fieldtype": "Select",
			"options":"\nBuddhism\nChristian\nHindu\nIslam\nJain\nOthers\nSikh",
			"width": "80",
			"reqd": 0,
			
		},
		{
			"fieldname":"cast",
			"label": __("Cast"),
			"fieldtype": "Select",
			"options":"\nSC\nST\nOther",
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
			"fieldname":"gender",
			"label": __("Gender"),
			"fieldtype": "Select",
			"options":"\nMale\nFemale\nOther",
			"width": "80",
			"reqd": 0,
			
		},
	]
};
