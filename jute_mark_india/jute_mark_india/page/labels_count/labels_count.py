import frappe

@frappe.whitelist()
def get_label_count(user):
    # user = frappe.session.user
    roles = frappe.get_roles(user)

    if frappe.session.user == "Administrator":
        query = """
            SELECT
                SUM(IFNULL(no_of_labels, 0)) as total_count
            FROM
                `tabOn-Site Verification Form`
        """
        label_count = frappe.db.sql(query, as_dict=1)
        if label_count:
            return label_count[0]['total_count'] if label_count[0]['total_count'] is not None else 0
        else:
            return 0
    elif "JMI User" in roles:
        user_full_name = frappe.get_value("User", user, "full_name")
        query = f"""
            SELECT
                no_of_labels as total_count
            FROM
                `tabOn-Site Verification Form`
            WHERE
                applicant_name LIKE %s
        """
        label_count = frappe.db.sql(query, (f'%{user_full_name}%',), as_dict=1)
        if label_count:
            return label_count[0]['total_count'] if label_count[0]['total_count'] is not None else 0
        else:
            return 0
    elif 'Regional Officer(RO)' in roles:
        user_full_name = frappe.get_value("User", user, "full_name")
        query = f"""
            SELECT
                COUNT(no_of_labels) as total_count
            FROM
                `tabOn-Site Verification Form`
            WHERE
                regional_office LIKE %s
	    """
        label_count = frappe.db.sql(query, (f'%{user_full_name}%',), as_dict=1)
        if label_count:
            return label_count[0]['total_count'] if label_count[0]['total_count'] is not None else 0
        else:
	        return 0
