import frappe
import os
import math
import random
import smtplib
from frappe import utils, _
import uuid
import base64
from frappe.core.doctype.user.user import sign_up as user_signup
import urllib.request
import urllib.parse
from frappe.core.doctype.sms_settings.sms_settings import send_sms

@frappe.whitelist(allow_guest=True)
def sign_up(phone):
    try:
        digits="0123456789"
        OTP=""

        for i in range(6):
            OTP+=digits[math.floor(random.random()*10)]
        otp = OTP

        users = frappe.get_all('User', fields=['name'], limit=1)

        create_table = frappe.db.sql("""
                        create table if not exists `User Register`(mobile_number varchar(200), otp int(15), id int NOT NULL AUTO_INCREMENT PRIMARY KEY);
        """)

        messages = "Dear User, OTP for  Login is : {}".format(otp)

        insert_values = frappe.db.sql("""
                        insert into `User Register`(`mobile_number`, `otp`) values('{}', {});
        """.format(phone, otp))

        return 1, _("OTP sent successfully")
    except:
        return 0
    # except:
    #     return 0, _('Something Went Wrong')

@frappe.whitelist(allow_guest=True)
# def verify_otp_for_profile_deletion(email_id, otp):
def verify_otp_for_profile_deletion(otp):

    validate_otp = frappe.db.sql("""
            select otp from `User Profile Delete`
            where email_id = '{}'
            order by id desc limit 1;
    # """.format())
    # """.format(email_id))

    if validate_otp and validate_otp[0][0] == int(otp):
        return 1
    else:
        return 0

@frappe.whitelist(allow_guest=True)
#def verify_otp(email_id, otp):
def verify_otp(otp):
    validate_otp = frappe.db.sql("""
            select otp from `User Register`
            order by id desc limit 1;
    """.format())
    if validate_otp[0][0] == int(otp):
        return 1, _('Your OTP has been verified successfully')
    else:
        return 0

@frappe.whitelist(allow_guest=True)
def user_creation(redirect_to, email_id, first_name,middle_name, last_name, mobile_no, registration_no, taluka, types_of_candidates, full_address):
    sign_up_response = user_signup(email_id, first_name, redirect_to)
    if sign_up_response[0] == 0:
        return sign_up_response

    candidate_info = frappe.new_doc('Jute Jute Mark India Registration form')
    candidate_info.first_name = first_name
    candidate_info.name = registration_no
    candidate_info.last_name = last_name
    candidate_info.mobile_no = mobile_no
    #job_candidate_info.candidate_type = candidate_type
    candidate_info.email_id = email_id
    candidate_info.taluka = taluka
    candidate_info.category = types_of_candidates
    #job_candidate_info.types_of_candidates = types_of_candidates
    candidate_info.save(ignore_permissions=True)

    user = frappe.get_doc("User", email_id)
    user.taluka = taluka
    user.middle_name = middle_name
    user.last_name = last_name
    user.mobile_no = mobile_no
    user.registration_no = registration_no

    # user.append('roles',{"doctype": "Has Role","role":"Job Candidate"})
    user.save(ignore_permissions=True)
    return sign_up_response,candidate_info.name

@frappe.whitelist(allow_guest=True)
def mobile_otp(number):
    data =  urllib.parse.urlencode({'apikey': 'NGI1NjYyNDI3NjRlNDg0YTRjNTgzNzQ1NDc2NTcxNTc=', 'numbers': number,
        'message' : 'message', 'sender': 'Priyanka'})
    data = data.encode('utf-8')
    request = urllib.request.Request("https://api.textlocal.in/send/?")
    f = urllib.request.urlopen(request, data)
    fr = f.read()
    return(fr)

@frappe.whitelist()
def redirect_to_home_page():
    return 'success'
