import frappe
import math
import random

@frappe.whitelist(allow_guest=True)
def register(email_id, mobile_number):
    try:
        digits="0123456789"
        otp=""
        for i in range(6):
            otp+=digits[math.floor(random.random()*10)]
        if not (frappe.db.exists('Jute Mark India Registration form', { 'mobile_number':mobile_number }) or frappe.db.exists('Jute Mark India Registration form', { 'email_id':email_id })):
            doc = frappe.new_doc('User Registration')
            doc.email_id = email_id
            doc.mobile_number = mobile_number
            doc.otp = otp
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return 1
        else:
            return 0
    except Exception as exception:
        frappe.log_error(frappe.get_traceback())

@frappe.whitelist(allow_guest=True)
def verify_otp(mobile_number, otp):
    try:
        otp_validated = 0
        if frappe.db.exists('User Registration', { 'mobile_number':mobile_number, 'verified':0 }):
            registration_doc, real_otp = frappe.db.get_value('User Registration', { 'mobile_number':mobile_number, 'verified':0 }, ['name', 'otp'])
            if str(otp) == str(real_otp):
                otp_validated = 1
                frappe.db.set_value('User Registration', registration_doc, 'verified', 1)
                frappe.db.commit()
        return otp_validated
    except Exception as exception:
        frappe.log_error(frappe.get_traceback())
