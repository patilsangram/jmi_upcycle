# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

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
        conditions += f" and jmi.date between '{filters.get('from_date')}' and '{filters.get('to_date')}'"

    if filters.get("category_b"):
        conditions += f" and jmi.category_b = '{filters.get('category_b')}'"

    if filters.get("district"):
        conditions += f" and jmi.district = '{filters.get('district')}'"

    if filters.get("gender"):
        conditions += f" and jmi.gender = '{filters.get('gender')}'"

    if filters.get("status"):
        conditions += f" and jmi.workflow_state = '{filters.get('status')}'"

    return conditions

def get_data(filters,conditions):
	# if filters and conditions:
	print(f"filters --- {filters}")
	data = frappe.db.sql(f""" SELECT DISTINCT
					*
	           	FROM 
					`tabJute Mark India Registration form` jmi
				WHERE 1=1 
                {conditions}
					
			""",as_dict=1,debug=1)
	return data 
	
def get_columns(filters):
    columns = [
        {
            "label": _("Application No."),
            "fieldname": "name",
            "fieldtype": "data",
            "width": 80,
        },
        {
            "label": _("Applicant"),
            "fieldname": "applicant_name",
            "fieldtype": "data",
            "width": 100,
        },
        {
            "label": _("Application Status"),
            "fieldname": "workflow_state",
            "fieldtype": "data",
            "width": 100,
        },

        {
            "label": _("Regional Office"),
            "fieldname": "district",
            "fieldtype": "data",
            "width": 80,
        },
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "date",
            "width": 80,
        },
        {
            "label": _("Category"),
            "fieldname": "category_b",
            "fieldtype": "data",
            "width": 80,
        },
        {
			"fieldname":"gender",
			"label":"Gender",
			"fieldtype": "Data",
			"width": 80,
		},

    ]
    return columns
