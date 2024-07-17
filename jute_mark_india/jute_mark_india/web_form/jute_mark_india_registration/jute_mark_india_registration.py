import frappe
import re

def get_context(context):
	pass

@frappe.whitelist(allow_guest=True)
def get_districts(state):
	if state:
		districts = frappe.db.get_all('District', filters={'state':state})
	else:
		districts = frappe.db.get_all('District')
	return districts

@frappe.whitelist(allow_guest=True)
def get_tahsil_taluka(district):
	if district:
		tahsil_talukas = frappe.db.get_all('TalukaTahsil', filters={'district':district})
	else:
		tahsil_talukas = frappe.db.get_all('TalukaTahsil')
	return tahsil_talukas

@frappe.whitelist(allow_guest=True)
def get_pincodes(district):
	if district:
		pincodes = frappe.db.get_all('Pincode', filters={'district':district})
	else:
		pincodes = frappe.db.get_all('Pincode')
	return pincodes

@frappe.whitelist(allow_guest=True)
def validate_mobile_number(mobile_no):
	if frappe.db.exists("Jute Mark India Registration form",{'mobile_number':mobile_no}):
		frappe.throw("Registration Form with this Mobile Number Already Exists")

@frappe.whitelist(allow_guest=True)
def validate_email(email_id):
	if frappe.db.exists("Jute Mark India Registration form",{'email_id':email_id}):
		frappe.throw("Registration Form with this Email Id Already Exists")


@frappe.whitelist(allow_guest=True)
def get_last_signup_data():
	'''
		Method to get details of last signup OTP
	'''
	if frappe.db.exists('User Registration', { 'verified':1 }):
		email_id, mobile_no = frappe.db.get_value('User Registration', { 'verified':1 }, ['email_id', 'mobile_number'])
		return { 'email_id':email_id, 'mobile_no':mobile_no }
	else:
		return 0
