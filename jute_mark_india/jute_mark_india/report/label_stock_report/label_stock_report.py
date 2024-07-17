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
        conditions += f" and lba.creation between '{filters.get('from_date')}' and '{filters.get('to_date')}'"
    if filters.get("district"):
    	conditions += f" and lba.regional_office = '{filters.get('district')}'"
    if filters.get("from_qr_code"):
    	conditions += f" and lba.from_qr_code = '{filters.get('from_qr_code')}'"
    if filters.get("to_qr_code"):
    	conditions += f" and lba.to_qr_code = '{filters.get('to_qr_code')}'"
    return conditions

def get_data(filters,conditions):
    data = frappe.db.sql(f""" SELECT DISTINCT
                lba.posting_date,lba.from_qr_code,lba.to_qr_code,lba.total_no_of_labels,
                lba.regional_office
            FROM `tabLabel Allocation` lba 
                    
            WHERE 1=1 
                {conditions}
                    
            """,as_dict=1,debug=1)
    print(f"\n data--{data}\n")
    from_qr = data[0]['from_qr_code']
    to_qr = data[0]['to_qr_code']

    print(f"\n\nfrom_qr--{from_qr}\n\nto_qr--{to_qr}\n\n")

    data1 = frappe.db.sql(f"""SELECT 
        name as label_series,status as label_status 
        FROM `tabJMI QR Code` 
        WHERE name between '{from_qr}' and '{to_qr}'
        """,as_dict=1,debug=1)

    print(f"\n\n data1--{data1}\n\n")
    
    for row1 in data1:
        for row in data:
            row1.update(row)
            # row1.update({'posting_date':(row.get('posting_date'))})

    return data1
	
def get_columns(filters):
    columns = [
    	{
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "date",
            "width": 120,
        },
        {
            "label": _("From Qr Code"),
            "fieldname": "from_qr_code",
            "fieldtype": "data",
            "width": 155,
        },
        {
            "label": _("To Qr Code"),
            "fieldname": "to_qr_code",
            "fieldtype": "data",
            "width": 155,
        },
        {
            "label": _("label_series"),
            "fieldname": "label_series",
            "fieldtype": "data",
            "width": 155,
        },
        {
            "label": _("label_status"),
            "fieldname": "label_status",
            "fieldtype": "data",
            "width": 155,
        },

        {
            "label": _("Total No of Labels"),
            "fieldname": "total_no_of_labels",
            "fieldtype": "data",
            "width": 150,
        },
        {
            "label": _("Regional Office"),
            "fieldname": "regional_office",
            "fieldtype": "data",
            "width": 150,
        },
    ]
    return columns