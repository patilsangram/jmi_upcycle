import copy
from collections import OrderedDict

import frappe
from frappe import _, qb
from frappe.query_builder import CustomFunction
from frappe.query_builder.functions import Max
from frappe.utils import date_diff, flt, getdate
import re


def execute(filters=None):
    columns = get_columns(filters)
    conditions = get_conditions(filters)
    data = get_data(filters,conditions)
    return columns, data, None

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date") and filters.get("to_date"):
        conditions += f" and lbe.creation between '{filters.get('from_date')}' and '{filters.get('to_date')}'"
    return conditions

def get_data(filters,conditions):
	data = frappe.db.sql(f""" SELECT DISTINCT
				lbe.creation,lbe.label_type,lbe.application_no,lbe.applicant_name,rlf.label_allotted,
				lbe.no_of_labels,lbe.required_no_of_labels,rlf.label_used,rlf.label_balanced
        	FROM `tabLabel Enhancement` lbe 
			JOIN `tabRequest For Label Fulfilment`rlf on lbe.on_site_verification= rlf.application_no		
			WHERE 1=1 
                {conditions}
					
			""",as_dict=1,debug=1)
	
	return data 
	
def get_columns(filters):
    columns = [
    	{
            "label": _("Date"),
            "fieldname": "creation",
            "fieldtype": "date",
            "width": 120,
        },
        {
            "label": _("Application No."),
            "fieldname": "application_no",
            "fieldtype": "data",
            "width": 120,
        },
        {
            "label": _("Applicant"),
            "fieldname": "applicant_name",
            "fieldtype": "data",
            "width": 100,
        },
        {
            "label": _("Labels alloted"),
            "fieldname": "label_allotted",
            "fieldtype": "data",
            "width": 150,
        },
        {
            "label": _("Labels Used"),
            "fieldname": "label_used",
            "fieldtype": "data",
            "width": 150,
        },
        {
            "label": _("Labels Balanced"),
            "fieldname": "label_balanced",
            "fieldtype": "data",
            "width": 150,
        },
        # {
        #     "label": _("Required Labels"),
        #     "fieldname": "required_no_of_labels",
        #     "fieldtype": "data",
        #     "width": 150,
        # },
    ]
    return columns