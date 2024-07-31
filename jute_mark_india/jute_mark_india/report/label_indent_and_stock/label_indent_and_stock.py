# Copyright (c) 2024, admin and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import has_common


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    return [
        {
            "label": _("Regional Office"),
            "fieldname": "regional_office",
            "fieldtype": "data",
            "width": 180,
        },
        {
            "label": _("Label Indent"),
            "fieldname": "label_indent",
            "fieldtype": "data",
            "width": 180,
        },
        {
            "label": _("Label Stock"),
            "fieldname": "label_stock",
            "fieldtype": "data",
            "width": 180,
        },
    ]


def get_data(filters):
    roles = frappe.get_roles()
    filter = ""
    if 'Regional Officer(RO)' in roles and ('HO' not in roles and frappe.session.user != "Administrator"):
        regional_office = frappe.db.get_value("User wise RO", frappe.session.user, "regional_office")
        if regional_office:
            filter = f"where a.regional_office='{regional_office}'"
        else:
            filter = "where 1=2"

    query = f"""
            SELECT
                COALESCE(a.regional_office, b.regional_office) AS regional_office,
                COALESCE(label_indent, 0) AS label_indent,
                COALESCE(label_stock, 0) AS label_stock
            FROM
                (SELECT regional_office, SUM(required_quantity) AS label_indent
                FROM `tabLabel Allocation`
                GROUP BY regional_office) AS a
            LEFT JOIN
                (SELECT allocated_to as regional_office, SUM(no_of_labels) AS label_stock
                FROM `tabRoll wise QR`
                GROUP BY allocated_to) AS b
            ON a.regional_office = b.regional_office {filter}
        """
    data = frappe.db.sql(query, as_dict=True)
    return data
