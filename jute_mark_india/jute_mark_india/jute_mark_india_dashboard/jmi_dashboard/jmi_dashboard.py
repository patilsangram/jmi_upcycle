import frappe

@frappe.whitelist()
def get_average_submission_time():
    average_submission_time = frappe.db.sql('''SELECT
                AVG(TIMESTAMPDIFF(SECOND, j.creation, c.creation)) AS average_submission_time
            FROM
                `tabComment` AS c
            JOIN
                `tabJute Mark India Registration form` AS j
            ON
                c.reference_name = j.name
            WHERE
                c.reference_doctype = 'Jute Mark India Registration form'
                AND c.comment_type = "Workflow"
                AND c.content = "Submitted";
            ''', as_dict=True)[0]['average_submission_time']/60.00
    return round(average_submission_time, 2)