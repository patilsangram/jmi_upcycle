import frappe
import json
from datetime import datetime,date

@frappe.whitelist(allow_guest=True)
def get_label_status(user):
    user_roles = frappe.get_roles(user)
    if 'JMI User' in user_roles and user != "Administrator":
        application_doc = frappe.get_doc("Jute Mark India Registration form",{'email_id':user})
        if application_doc.workflow_state == 'Approved By RO' or application_doc.workflow_state =='Approved By HO':
            if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':application_doc.name}):
                no_of_labels = frappe.db.get_value("On-Site Verification Form",{'textile_registration_no':application_doc.name},['no_of_labels'])
                app_date = application_doc.date
                todays_date = date.today()
                cur_year = todays_date.year
                if app_date.year == cur_year:
                    labels_per_month = int(no_of_labels/12)
                    if app_date.day>=25:
                        months = 12-app_date.month
                    else:
                        months = 12-app_date.month+1
                    total_labels = months*labels_per_month
                    if total_labels%10 != 0:
                        total_labels += 10-(total_labels%10)
                else:
                    total_labels = no_of_labels
                #return int(labels)
                data = frappe.db.sql("""select sum(required_qty) as total from `tabRequest for Label` where requested_by = '{0}' and docstatus=1 and EXTRACT(YEAR FROM posting_date) = '{1}' """.format(user,cur_year),as_dict=1)
                if not data[0].total:
                    used_labels = 0
                else:
                    used_labels = data[0].total
                unused_labels= total_labels - used_labels
                return (int(total_labels),int(used_labels),int(unused_labels))
                
            else:
                frappe.throw("On-Site Verification form is not created yet for user")
        else:
            frappe.throw("Jute Mark India Registration form  is not Approved ")
    elif 'Regional Officer(RO)' in user_roles and user != "Administrator":
        if frappe.db.exists("User wise RO",user):
            regional_office = frappe.get_doc("User wise RO",user).regional_office
            print("\n\n regional_office ==>",regional_office)
            data = frappe.db.sql("""select sum(total_no_of_labels) as total  from `tabLabel Allocation` where  requested_by = '{0}' and docstatus=1 """.format(user),as_dict=1)
            if not data[0].total:
                total_labels = 0
            else:
                total_labels = data[0].total
            available_labels = len(frappe.db.get_list("JMI QR Code",{'allocated_to_user':user}))
            data1 = frappe.db.sql(""" select sum(total_no_of_labels) as total  from`tabLabel Allocation` where regional_office='{0}' and Requested_by != '{1}' and docstatus=1; """.format(regional_office,user),as_dict=1)
            if not data1[0].total:
                used_labels = 0
            else:
                used_labels = data1[0].total
            return (int(total_labels),int(used_labels),int(available_labels))
        else:
            frappe.throw(_("Please Add {0} in to User wise RO".format(user)))
    elif user == "Administrator":
        total_labels = len(frappe.db.get_list("JMI QR Code"))
        used_labels = len(frappe.db.get_list("JMI QR Code", {"status": "Allocated to RO"}))
        available_labels = total_labels - used_labels
        return (int(total_labels), int(used_labels), int(available_labels))
