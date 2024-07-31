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
        conditions += f" and usr.creation between '{filters.get('from_date')}' and '{filters.get('to_date')}'"

    if filters.get("cast"):
        conditions += f" and jmi.category__scst_other_in_case_b_is_1 = '{filters.get('cast')}'"

    if filters.get("district"):
        conditions += f" and jmi.district = '{filters.get('district')}'"

    if filters.get("gender"):
        conditions += f" and jmi.gender = '{filters.get('gender')}'"

    if filters.get("religion"):
        conditions += f" and jmi.religion = '{filters.get('religion')}'"

    if filters.get("status")=='Active':
    	conditions += f" and usr.enabled = 1"
    if filters.get("status")=='Inactive':
    	conditions += f" and usr.enabled = 0"

    return conditions

def get_data(filters,conditions):
	data = frappe.db.sql(f""" SELECT DISTINCT
					jmi.applicant_name as applicant_name,jmi.name as application_name,jmi.religion,
					jmi.date as application_date,jmi.district as district,jmi.gender as gender,
					jmi.category_b,usr.enabled as usr_status,usr.name as email_id,jmi.category__scst_other_in_case_b_is_1 as cast
	           	FROM 
					`tabJute Mark India Registration form` jmi
				JOIN `tabUser` usr 
				ON jmi.email_id = usr.name
				WHERE 1=1 
                {conditions}
					
			""",as_dict=1,debug=1)
	for row in data:
		if row.get('usr_status')== 0 :
			row.update({'usr_status':'Inactive'})
		if row.get('usr_status')== 1 :
			row.update({'usr_status':'Active'})

	return data 
	
def get_columns(filters):
    columns = [
        {
            "label": _("Application No."),
            "fieldname": "application_name",
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
            "label": _("Religion"),
            "fieldname": "religion",
            "fieldtype": "data",
            "width": 150,
        },
        {
            "label": _("Cast"),
            "fieldname": "cast",
            "fieldtype": "data",
            "width": 100,
        },
		# {
  #           "label": _("User Email"),
  #           "fieldname": "email_id",
  #           "fieldtype": "data",
  #           "width": 150,
  #       },
        {
            "label": _("User Status"),
            "fieldname": "usr_status",
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
            "fieldname": "application_date",
            "fieldtype": "date",
            "width": 120,
        },
        {
            "label": _("Category"),
            "fieldname": "category_b",
            "fieldtype": "data",
            "width": 120,
        },
        {
			"fieldname":"gender",
			"label":"Gender",
			"fieldtype": "Data",
			"width": 100,
		},

    ]
    return columns
