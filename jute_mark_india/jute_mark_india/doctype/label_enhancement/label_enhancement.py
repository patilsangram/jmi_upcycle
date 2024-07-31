# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from jute_mark_india.api.mobile_api import *
from jute_mark_india.jute_mark_india.utils import *
from frappe.utils import flt
from frappe import _

class LabelEnhancement(Document):
	def validate(self):
		self.validate_on_site_verification()
		self.validate_current_label_count()
		self.validate_new_label_count()
		self.validate_assign_vo()
		self.validate_vo_assignment()

		if self.workflow_state == "Pending":
			frappe.db.set_value("Jute Mark India Registration form",self.application_no,"application_label_enhancement",1)
			frappe.db.commit()

		if self.workflow_state=="Assigned VO" and self.label_type=="Permanent":
			self.update_jute_Mark_india_registration_forms()
			
		
		if self.workflow_state == "Approved" and self.label_type=="Temporary":
			frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "label_enhancement", self.name)
			frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "no_of_label_requested", self.required_no_of_labels)
			frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "no_of_labels", self.required_no_of_labels)
			frappe.db.set_value('On-Site Verification Form',self.on_site_verification,'no_of_label_approved',self.required_no_of_labels)
			frappe.db.set_value("Jute Mark India Registration form",self.application_no,"application_label_enhancement",0)
			frappe.db.commit()

		if self.workflow_state == "Rejected" and self.label_type=="Temporary":
			frappe.db.set_value("Jute Mark India Registration form",self.application_no,"application_label_enhancement",0)
			frappe.db.commit()

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

	def validate_on_site_verification(self):
		if self.application_no:
			on_site_verification = get_on_site_verification_form(self.application_no)
			if on_site_verification:
				self.on_site_verification = on_site_verification
				self.no_of_labels = frappe.db.get_value('On-Site Verification Form', on_site_verification, 'no_of_labels')
			else:
				frappe.throw('On Site Verification form not yet created!')

	def validate_new_label_count(self):
		if self.required_no_of_labels:
			validated = validate_label_count(self.required_no_of_labels)
			if not validated:
				frappe.throw('Required No Of Labels should be multiple of 10!')
			else:
				if self.required_no_of_labels < self.no_of_labels:
					frappe.throw('Required no. of Labels is less than current label count!')
		else:
			frappe.throw('Required No Of Labels should be multiple of 10!')

	def validate_current_label_count(self):
		if not self.no_of_labels:
			frappe.throw('Please contact your Regional Officer, Since no labels allocated for this application!')

	def on_update_after_submit(self):
		if self.workflow_state == 'Approved':
			if self.label_type == 'Temporary':
				frappe.db.set_value('On-Site Verification Form', self.on_site_verification, 'no_of_labels', self.required_no_of_labels)
				frappe.db.set_value('On-Site Verification Form', self.on_site_verification, 'label_type', 'Temporary')
				frappe.db.set_value('On-Site Verification Form', self.on_site_verification, 'attachment_for_label', self.attachment_for_label)
				frappe.db.commit()
				frappe.msgprint('Labels Enhanced Successfully.', indicator='green', alert=True)
			elif self.label_type == "Permanent":
				frappe.db.set_value('Jute Mark India Registration form',self.application_no,'application_label_enhancement',0)
				frappe.db.commit()


	def validate_assign_vo(self):
		if self.workflow_state == "Draft" and self.label_type == "Permanent":
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


	def update_jute_Mark_india_registration_forms(self):
		frappe.db.set_value("Jute Mark India Registration form", self.application_no, "workflow_state", "Assigned VO")
		frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "workflow_state", "Assign VO")
		frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "label_enhancement", self.name)
		frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "no_of_label_requested", self.required_no_of_labels)
		frappe.db.set_value('On-Site Verification Form',self.on_site_verification,'no_of_label_approved',0)
		frappe.db.set_value("Jute Mark India Registration form", self.application_no, "label_check",1)
		frappe.db.commit()
		doc = frappe.get_doc("Jute Mark India Registration form", self.application_no)
		# doc.workflow_state = "Application Submitted"
		# doc.save(ignore_permissions=True)
		# frappe.db.commit()
		assign_count = 0
		for row in self.assign_vo_for_sites:
			if row.assign_to:
				assign_count += 1
				desc = "Assigned site for Label Enhancement :" + self.name +"- Address : " + row.name_of_unit__outlet + ", " + row.address 
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
@frappe.validate_and_sanitize_search_inputs
def get_users(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(
		"""select a.name, a.full_name from `tabUser` as a left join `tabHas Role` as b on a.name=b.parent
		where  b.role = 'Verification Officer(VO)' and a.name like %(txt)s
		order by
			if(locate(%(_txt)s, a.name), locate(%(_txt)s, a.name), 99999),
			a.name asc
		limit {start}, {page_len}""".format(
			start=start, page_len=page_len
		),
		{
			"txt": "%{0}%".format(txt),
			"_txt": txt.replace("%", "")
		},
	)


@frappe.whitelist()
def get_permission_query_conditions(user):
	'''
	Permission Query conditions for Label Enhancement
	'''
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	conditions = False
	if user != "Administrator":
		if "Verification Officer(VO)" in user_roles:
			applications = frappe.db.sql("""select le.name from `tabLabel Enhancement` le join `tabLabel Enhancement VO Assignment` a on le.name = a.parent  where a.assign_to = '{0}' """.format(user),as_dict=1)

			l1 = "(" + ",".join("'{0}'".format(app.get("name")) for app in applications) + ")"
			if len(applications) >= 1:
				conditions = '`tabLabel Enhancement`.`name` in {0}'.format(l1)
			else:
				conditions = '`tabLabel Enhancement`.`name` = "00000" '

		if "Regional Officer(RO)" in user_roles:
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			app_list = frappe.db.sql(""" select name from `tabJute Mark India Registration form` where regional_office = '{0}' """.format(regional_office),as_dict=1)
			l1 = "(" + ",".join("'{0}'".format(app.get("name")) for app in app_list) + ")"
			if len(app_list) >= 1:
				conditions = '`tabLabel Enhancement`.`application_no` in {0}'.format(l1)
			else:
				conditions = '`tabLabel Enhancement`.`name` = "00000" '
			
			#out = [item for t in app_list for item in t]
			# if len(out) == 1:
			# 	item = out[0]
			# 	conditions = '`tabLabel Enhancement`.`application_no` like "%{item}%"'.format(item=item)
			# else:
			# 	conditions = '`tabLabel Enhancement`.`application_no` in {0}'.format(tuple(out))

			# reg_app = frappe.db.sql("""SELECT name FROM `tabJute Mark India Registration form` where _assign='{0}' or owner='{0}' """.format(user), as_dict=1)
			# app_list ="(" + ",".join("'{0}'".format(app.get("name")) for app in reg_app) + ")"
			# if len(app_list)>2:
			# 	conditions = '`tabLabel Enhancement`.`application_no` in {0}'.format(app_list)

		if 'JMI User' in user_roles:
			conditions = '`tabLabel Enhancement`.`owner` like "%{user}%"'.format(user=user)
		return conditions
