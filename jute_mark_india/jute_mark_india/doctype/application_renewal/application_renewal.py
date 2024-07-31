# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from jute_mark_india.api.mobile_api import *
from jute_mark_india.jute_mark_india.utils import *
from frappe.utils import flt
from frappe.utils import  add_years

class ApplicationRenewal(Document):
	def validate(self):
		app_renew = frappe.get_doc("Jute Mark India Registration form",self.application_no).application_renewal
		#renewal_date = add_years(getdate(row.get("application_date")), years)
		if not app_renew:
			frappe.throw("You cannot do Renewal, Your Application Valid till today!!")

		if(self.workflow_state == "Pending"):
			user_role = frappe.get_roles(frappe.session.user)
			if not self.is_paid and "JMI User" in user_role:
				frappe.throw("Please Proceed Payment First !")

		self.validate_assign_vo()
		self.validate_vo_assignment()

		if self.workflow_state=="Assigned VO":
			self.update_jute_Mark_india_registration_forms()

	@frappe.whitelist()
	def get_amount(self):
		amount = 0
		jmi_application = frappe.get_doc("Jute Mark India Registration form", self.application_no)
		fees_list = frappe.get_list("Fees Records", filters={"fees_description": "Renewal", "category": jmi_application.category_b})
		if fees_list:
			for i in fees_list:
				amount = frappe.get_value("Fees Records", i.name, "amount" ) 
		return amount
	
	def update_jute_Mark_india_registration_forms(self):
		frappe.db.set_value("Jute Mark India Registration form", self.application_no, "workflow_state", "Assigned VO")
		frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "workflow_state", "Assign VO")
		frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "application_renewal", self.name)
		frappe.db.commit()
		doc = frappe.get_doc("Jute Mark India Registration form", self.application_no)
		assign_count = 0
		for row in self.assign_vo_for_sites:
			if row.assign_to:
				assign_count += 1
				desc = "Assigned site for Application Renewal:" + self.name +"- Address : " + row.name_of_unit__outlet + ", " + row.address
				if not frappe.db.exists("ToDo", { "allocated_to": row.assign_to, "reference_type":"Jute Mark India Registration form", "reference_name":self.application_no, "description":desc }):
					create_todo(row.assign_to, desc, "Jute Mark India Registration form", self.application_no)
					if assign_count == 1:
						primary_site = frappe.get_doc('Actual Site Visit Plan', { 'application_no':self.application_no, 'is_primary_site':1 }).name
						frappe.db.set_value("Actual Site Visit Plan",primary_site,'is_primary_site',0)
						frappe.db.commit()
						site_visit_id = schedule_site_visit(self.application_no, row.name_of_unit__outlet, row.assign_to, row.address,row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan,1)
					else:
						site_visit_id = schedule_site_visit(self.application_no, row.name_of_unit__outlet, row.assign_to, row.address, row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan)
					row.site_visit_id = site_visit_id


	@frappe.whitelist()
	def validate_vo_assignment(self):
		if self.workflow_state == "Assigned VO":
			vo_assignment_count = 0
			for row in self.assign_vo_for_sites:
				if row.assign_to:
					vo_assignment_count += 1
			if vo_assignment_count == 0:
				frappe.throw('Atleast one site should Assign to VO!')
			if vo_assignment_count > 5:
				frappe.throw('Maximum of 5 site can be Assignned to VO!')

	def validate_assign_vo(self):
		if self.workflow_state == "Draft" and self.is_new():
			doc = frappe.get_doc("Jute Mark India Registration form", self.application_no)
			if doc.category_b == "Artisan":
				no_male = 0
				no_female = 0
				no_other = 0
				if doc.gender == "Male":
					no_male = 1
				elif doc.gender == "Female":
					no_female = 1
				else:
					no_other = 1
				self.append('assign_vo_for_sites',{
					'name_of_unit__outlet' : doc.address_line_1,
					'address': doc.address_line_1,
					'no_of_male_artisan' : no_male,
					'no_of_female_artisan' : no_female,
					'no_of_other_artisan' : no_other
					})
			else :
				for row in doc.textile_details_of_production_units_or_retailer_sales_outlets:
					self.append('assign_vo_for_sites',{
						'name_of_unit__outlet' : row.name_of_unit__outlet,
						'address':row.address,
						'no_of_male_artisan' : row.no_of_male_artisan,
						'no_of_female_artisan' : row.no_of_female_artisan,
						'no_of_other_artisan' : row.no_of_other_artisan
					})


@frappe.whitelist()
def get_permission_query_conditions(user):
	'''
	Permission Query conditions for Application Renewal
	'''
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	conditions = False
	if user != "Administrator":
		if "Verification Officer(VO)" in user_roles:
			applications = frappe.db.sql("""select a.name from `tabApplication Renewal` a join `tabLabel Enhancement VO Assignment` v on a.name = v.parent where  v.parenttype = "Application Renewal" and v.assign_to = '{0}' """.format(user),as_dict=1)

			l1 = "(" + ",".join("'{0}'".format(app.get("name")) for app in applications) + ")"
			if len(applications) >= 1:
				conditions = '`tabApplication Renewal`.`name` in {0}'.format(l1)
			else:
				conditions = '`tabApplication Renewal`.`name` = "00000" '
		if "Regional Officer(RO)" in user_roles:
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			app_list = frappe.db.sql(""" select name from `tabJute Mark India Registration form` where regional_office = '{0}' """.format(regional_office),as_dict=1)

			l1 = "(" + ",".join("'{0}'".format(app.get("name")) for app in app_list) + ")"
			if len(app_list) >= 1:
				conditions = '`tabApplication Renewal`.`application_no` in {0}'.format(l1)
			else:
				conditions = '`tabApplication Renewal`.`name` = "00000" '

			# reg_app = frappe.db.sql("""SELECT name FROM `tabJute Mark India Registration form` where _assign='{0}' or owner='{0}' """.format(user), as_dict=1)
			# app_list ="(" + ",".join("'{0}'".format(app.get("name")) for app in reg_app) + ")"
			# if len(app_list)>2:
			# 	conditions = '`tabApplication Renewal`.`application_no` in {0}'.format(app_list)

		if 'JMI User' in user_roles:
			conditions = '`tabApplication Renewal`.`owner` like "%{user}%"'.format(user=user)
		return conditions
