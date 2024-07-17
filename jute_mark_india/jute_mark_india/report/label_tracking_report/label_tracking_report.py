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
        conditions += f" and qrl.creation between '{filters.get('from_date')}' and '{filters.get('to_date')}'"

    # if filters.get("cast"):
    #     conditions += f" and jmi.category__scst_other_in_case_b_is_1 = '{filters.get('cast')}'"

    # if filters.get("district"):
    #     conditions += f" and jmi.district = '{filters.get('district')}'"

    # if filters.get("gender"):
    #     conditions += f" and jmi.gender = '{filters.get('gender')}'"

    # if filters.get("religion"):
    #     conditions += f" and jmi.religion = '{filters.get('religion')}'"

    # if filters.get("status")=='Active':
    # 	conditions += f" and usr.enabled = 1"
    # if filters.get("status")=='Inactive':
    # 	conditions += f" and usr.enabled = 0"

    return conditions

def get_data(filters,conditions):
	data = frappe.db.sql(f""" SELECT DISTINCT
					*	
				FROM 
					`tabJMI QR View Log` qrl
				
				WHERE 1=1 
                {conditions}
					
			""",as_dict=1,debug=1)
	
	return data 
	
def get_columns(filters):
    columns = [
        {
            "label": _("Label No."),
            "fieldname": "jmi_qr_code",
            "fieldtype": "data",
            "width": 120,
        },
        {
            "label": _("User"),
            "fieldname": "user",
            "fieldtype": "data",
            "width": 100,
        },
        {
            "label": _("Region"),
            "fieldname": "user_location",
            "fieldtype": "data",
            "width": 150,
        },
        {
            "label": _("Latitude"),
            "fieldname": "latitude",
            "fieldtype": "data",
            "width": 100,
        },
        {
            "label": _("Longitude"),
            "fieldname": "longitude",
            "fieldtype": "data",
            "width": 100,
        },

        {
            "label": _("User Location"),
            "fieldname": "user_ip_address",
            "fieldtype": "data",
            "width": 80,
        },
        
    ]
    return columns
