# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.mapper import *
from frappe.model.naming import make_autoname
from jute_mark_india.api.mobile_api import validate_label_count
from frappe import _
from datetime import datetime,date
from jute_mark_india.jute_mark_india.notifications import send_notification

class RequestforLabel(Document):
	def autoname(self):
		if self.regional_office:
			series = 'LABEL-REQ-'+self.regional_office+'-'
			self.name = make_autoname(series)

	def validate(self):
		self.validate_required_qty()
		self.validate_qty_for_prorata()

	def validate_required_qty(self):
		if self.required_qty:
			validated = validate_label_count(self.required_qty)
			if not validated:
				frappe.throw('Required Qty should be multiple of 10!')
			else:
				if self.required_qty < 50:
					frappe.throw('Minimum 50 Qty is required!')
		else:
			frappe.throw('Required Qty is required!')

	def validate_qty_for_prorata(self):
		if not self.is_ro:
			user = frappe.session.user
			application_doc = frappe.get_doc("Jute Mark India Registration form",{'email_id':self.requested_by})
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
						labels = months*labels_per_month
						if labels%10 != 0:
							labels += 10-(labels%10)
					else:
						labels = no_of_labels
					data = frappe.db.sql(""" select sum(required_qty) as total from `tabRequest for Label` where requested_by = '{0}' and docstatus=1 and EXTRACT(YEAR FROM posting_date) = '{1}' """.format(user,cur_year),as_dict=1)
					if not data[0].total:
						used_labels = 0
					else:
						used_labels = data[0].total
					unused_labels= labels - used_labels
					if self.required_qty > unused_labels:
						frappe.throw(_("Your remaining balance of label is : {0} Only".format(int(unused_labels))))
				else:
					frappe.throw(_("On-Site Verification Form is not available for email :{0}".format(self.requested_by)))
			else:
				frappe.throw(_("Jute Mark India Registration form with id : '{0}' is not Approved ".format(application_doc.name)))

	def on_submit(self):
		user_role = frappe.get_roles(frappe.session.user)
		if not self.is_paid and "JMI User" in user_role:

			frappe.throw("Please Proceed Payment First !")
		if self.requested_by and self.app__reg_number:
			send_notification(self.doctype, self.name, 'Label Enhancement Notification', self.requested_by)

	@frappe.whitelist()
	def get_amount(self):
		amount = 0
		jmi_application = frappe.get_doc("Jute Mark India Registration form", self.jmi_registration_form)

		fees_list = frappe.get_list("Fees Records", filters={"fees_description": "Label Request", "category": jmi_application.category_b})
		if fees_list:
			for i in fees_list:
				rate = frappe.get_value("Fees Records", i.name, "amount" ) 
				amount = rate * self.required_qty
		return amount
	
@frappe.whitelist()
def create_label_allocation(source_name, target_doc = None):
	'''Method to create Label Allocation'''
	def set_missing_values(source, target):
		target.regional_office = source.regional_office
		target.required_quantity = source.required_qty
		data = frappe.db.sql(""" select sum(requested_quantity) as qty1 from `tabLabel Allocation` where request_for_label='{}' and docstatus=1""".format(source.name),as_dict=1)
		if not data[0].qty1 :
			data[0].qty1 =  0
		balance_qty = source.required_qty - data[0].qty1
		target.requested_quantity = balance_qty
	doc = get_mapped_doc(
		'Request for Label',
		source_name,
		{
			'Request for Label': {
				'doctype': 'Label Allocation',
			},
		}, target_doc, set_missing_values)
	return doc

@frappe.whitelist()
def is_label_allocation_exist(request_for_label,qty):
	'''Method to check wether Label Allocation is created or not'''
	label_allocation_exist = False
	data = frappe.db.sql(""" select sum(requested_quantity) as qty1 from `tabLabel Allocation` where request_for_label='{}' and docstatus=1""".format(request_for_label),as_dict=1)
	if data[0].qty1 == int(qty):
		label_allocation_exist = True
	return label_allocation_exist

@frappe.whitelist()
def set_regional_office(user):
	if frappe.db.exists("User",user):
		user_doc = frappe.get_doc("User",user)
		roles = frappe.db.sql("""select role from `tabHas Role` where parent = '{0}' and parenttype='User'  """.format(user),as_dict=1)
		if any(d['role'] == 'Regional Officer(RO)' for d in roles):
			if not frappe.db.exists("User wise RO",user):
				frappe.throw(_("Please add Regional Office for User :{0} in Doctype : User wise RO").format(user))
			else:
				regional_office = frappe.db.get_value("User wise RO", user,'regional_office')
				return regional_office
		elif any(d['role'] == 'JMI User' for d in roles):
			if not frappe.db.exists("Jute Mark India Registration form",{'email_id':user}):
				frappe.throw("Regional Office not present as Registration Id not generated yet")
			else:
				regional_office = frappe.db.get_value("Jute Mark India Registration form",{'email_id':user},'regional_office')
				return regional_office

@frappe.whitelist()
def get_permission_query_conditions_request_label(user):
	'''
	Permission Query conditions for Jute Mark India Reg Form
	'''
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	conditions = False
	if user != "Administrator":
		if 'Regional Officer(RO)' in user_roles:
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			conditions = '`tabRequest for Label`.`regional_office` like "%{regional_office}%" '.format(regional_office = regional_office)
		elif 'JMI User' in user_roles:
			conditions = '`tabRequest for Label`.`requested_by` like "%{user}%" '.format(user = user)

	else:
		conditions = '`tabRequest for Label` .`is_ro` like "1" ';
	return conditions

@frappe.whitelist()
def create_ro_transfer(source_name, target_doc = None):
	'''Method to create Label Allocation for RO to RO Transfer'''
	def set_missing_values(source, target):
		target.regional_office = source.regional_office
		target.required_quantity = source.required_qty
		target.is_ro_transfer = 1
		data = frappe.db.sql(""" select sum(requested_quantity) as qty1 from `tabLabel Allocation` where request_for_label='{}' and docstatus=1""".format(source.name),as_dict=1)
		if not data[0].qty1 :
			data[0].qty1 =  0
		balance_qty = source.required_qty - data[0].qty1
		target.requested_quantity = balance_qty
		#target.requested_quantity = source.required_qty
	doc = get_mapped_doc(
		'Request for Label',
		source_name,
		{
			'Request for Label': {
				'doctype': 'Label Allocation',
			},
		}, target_doc, set_missing_values)
	return doc
