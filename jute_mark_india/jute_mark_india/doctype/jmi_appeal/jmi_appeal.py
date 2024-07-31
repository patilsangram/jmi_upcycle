# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import *
from frappe.model.document import Document
from jute_mark_india.jute_mark_india.utils import *
from frappe.utils import flt
from datetime import datetime,date

class JMIAppeal(Document):
	def validate(self):
		if not self.user_id:
			self.user_id = frappe.session.user
		self.validate_appeal_date()
		self.check_duplicate_appeals()
		self.validate_assign_vo()
		self.validate_vo_assignment()

		if self.workflow_state=="Assigned VO":
			self.update_jute_Mark_india_registration_forms()
		if self.workflow_state=="Approved" or self.workflow_state == "Rejected":

			frappe.db.set_value("On-Site Verification Form", {"textile_registration_no":self.application_no}, "jmi_appeal", self.name)
			#frappe.db.set_value("On-Site Verification Form", {"textile_registration_no":self.application_no}, "no_of_label_requested", self.no_of_label_requested)
			#frappe.db.set_value("On-Site Verification Form", self.on_site_verification, "no_of_labels", self.no_of_label_requested)
			frappe.db.commit()
		user = frappe.session.user
		print("\n\n user --> appeal doc-->",user)
		roles = frappe.get_roles(user)
		if "Regional Officer(RO)" in roles and self.workflow_state == "Approved":
			print("\n\n ****************** inside ro level ******************\n\n ")
			frappe.db.set_value("Jute Mark India Registration form",{'name':self.application_no},"workflow_state","Approved By RO")
		elif "HO" in roles and self.workflow_state == "Approved":
			print("\n\n user --->HO level ")
			frappe.db.set_value("Jute Mark India Registration form",{'name':self.application_no},"workflow_state","Approved By HO")




	def validate_appeal_date(self):
		''' Method to Validate Appeal Dates '''
		if self.appeal_type:
			if self.appeal_type != 'Appeal for Escalation':
				jmi_modified_date = frappe.get_doc("Jute Mark India Registration form",self.application_no).modified
				#print("\n\n jmi_modified_date ===>",jmi_modified_date)
				if getdate(self.appealing_date) >= getdate(frappe.utils.add_to_date(jmi_modified_date, days=15)):
					frappe.throw("Appealing date is expired!!")
			else:
				if getdate(self.appealing_date) < getdate(frappe.utils.add_to_date(self.previous_appealing_date, days=7)):
					frappe.throw("Appeal for Escalation can only be created after 7 Days of Appeal!!")
		else:
			frappe.throw("Appeal Type is required!!")

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
		if self.workflow_state == "Draft":
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
	def get_application_for_esacalation(self):
		''' Method to get Application details from Appeal '''
		application_data = {}
		if self.jmi_appeal:
			application_no, applicant_name, application_date = frappe.db.get_value('JMI Appeal', self.jmi_appeal, ['application_no', 'applicant_name', 'application_date'])
			application_data = {
				'application_no':application_no,
				'applicant_name':applicant_name,
				'application_date':application_date,
			}
		return application_data

	def check_duplicate_appeals(self):
		''' Method to check wether duplicate Appeal exists for same Application '''
		if frappe.db.exists('JMI Appeal', { 'application_no': self.application_no, 'appeal_type':self.appeal_type, 'name':['!=', self.name] }):
			frappe.throw("Appeal is Already created against this appplication!!")


	def update_jute_Mark_india_registration_forms(self):
		print("\n\n -------------------Inside update_jute_Mark_india_registration_forms --------------------jmi Appeal\n\n")
		frappe.db.set_value("Jute Mark India Registration form", self.application_no, "workflow_state", "Assigned VO")
		#frappe.db.set_value("On-Site Verification Form", {"textile_registration_no":self.application_no}, "workflow_state", "Assign VO")
		frappe.db.set_value("On-Site Verification Form", {"textile_registration_no":self.application_no}, "jmi_appeal", self.name)
		#frappe.db.set_value("On-Site Verification Form", {"textile_registration_no":self.application_no}, "no_of_label_requested", self.no_of_label_requested)
		frappe.db.commit()
		doc = frappe.get_doc("Jute Mark India Registration form", self.application_no)
		assign_count = 0
		for row in self.assign_vo_for_sites:
			print("\n\n ****************row of assign vo for sites**************")
			if row.assign_to:
				assign_count += 1
				print("\n\n assign_count ==>",assign_count)
				desc = "Assigned site for Appeal for Rejection:" + self.name +"- Address : " + row.name_of_unit__outlet + ", " + row.address
				if not frappe.db.exists("ToDo", { "allocated_to": row.assign_to, "reference_type":"Jute Mark India Registration form", "reference_name":self.application_no, "description":desc }):
					create_todo(row.assign_to, desc, "Jute Mark India Registration form", self.application_no)

					if assign_count == 1:
						primary_site = frappe.get_doc('Actual Site Visit Plan', { 'application_no':self.application_no, 'is_primary_site':1 }).name
						print("\n\n previous primary_site===>",primary_site)
						frappe.db.set_value("Actual Site Visit Plan",primary_site,'is_primary_site',0)
						frappe.db.commit()
						print("\n\n *******************making primary site ************\n\n",row.name_of_unit__outlet)
						site_visit_id = schedule_site_visit(self.application_no, row.name_of_unit__outlet, row.assign_to, row.address,row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan,1)
						print("\n\n**********site_visit_id===>",site_visit_id)
					else:
						print("\n\n *******************making other site NOT PRIMARY ************\n\n",row.name_of_unit__outlet)
						site_visit_id = schedule_site_visit(self.application_no, row.name_of_unit__outlet, row.assign_to, row.address, row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan)
					row.site_visit_id = site_visit_id

		# for row in doc.textile_details_of_production_units_or_retailer_sales_outlets:
		# 	''' To Assign Sites from Child Table '''
		# 	if row.assign_to:
		# 		desc = "Assigned site - Address : " + row.address
		# 		if row.idx == 1:
		# 			site_visit_id = schedule_site_visit(self.application_no, row.name_of_unit__outlet, row.assign_to, row.address, row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan, 1)
		# 		else:
		# 			site_visit_id = schedule_site_visit(self.application_no, row.name_of_unit__outlet, row.assign_to, row.address, row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan)
		# 			row.site_visit_id = site_visit_id


@frappe.whitelist()
def get_permission_query_conditions(user):
	'''
	Permission Query conditions for JMI Appeal
	'''
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	conditions = False
	if user != "Administrator":
		if "Verification Officer(VO)" in user_roles:
			applications = frappe.db.sql("""select le.name from `tabJMI Appeal` le join `tabLabel Enhancement VO Assignment` a on le.name = a.parent  where  a.parenttype = "JMI Appeal" and a.assign_to = '{0}' """.format(user),as_dict=1)

			l1 = "(" + ",".join("'{0}'".format(app.get("name")) for app in applications) + ")"
			if len(applications) >= 1:
				conditions = '`tabJMI Appeal`.`name` in {0}'.format(l1)
			else:
				conditions = '`tabJMI Appeal`.`name` = "00000" '

		if "Regional Officer(RO)" in user_roles:
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			app_list = frappe.db.sql(""" select name from `tabJute Mark India Registration form` where regional_office = '{0}' """.format(regional_office),as_dict=1)

			l1 = "(" + ",".join("'{0}'".format(app.get("name")) for app in app_list) + ")"
			if len(app_list) >= 1:
				conditions = '`tabJMI Appeal`.`application_no` in {0}'.format(l1)
			else:
				conditions = '`tabJMI Appeal`.`name` = "00000" '

		if 'JMI User' in user_roles:
			conditions = '`tabJMI Appeal`.`owner` like "%{user}%"'.format(user=user)
		return conditions





@frappe.whitelist()
def calculate_label_balance(application_no, user):
	label_balance = 0.0
	labels = 0.0
	used_labels = 0.0
	application_doc = frappe.get_doc("Jute Mark India Registration form",{'name':application_no})
	no_of_labels = frappe.db.get_value("On-Site Verification Form", {'textile_registration_no':application_no}, 'no_of_labels')
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
	data = frappe.db.sql("""select sum(required_qty) as total from `tabRequest for Label` where requested_by = '{0}' and docstatus=1 and EXTRACT(YEAR FROM posting_date) = '{1}' """.format(user,cur_year),as_dict=1)
	if not data[0].total:
		used_labels = 0
	else:
		used_labels = data[0].total
	label_balance = labels - used_labels
	return {"label_balance": int(label_balance), "no_of_labels":int(labels)}


@frappe.whitelist(allow_guest=True)
def get_registration_form_no(user,appeal_type):
    '''
        Method to get on application id  from user
       user: User
    '''
    roles = frappe.db.sql("""select role from `tabHas Role` where parent = '{0}' and parenttype='User'  """.format(user),as_dict=1)
    if any(d['role'] == 'JMI User' for d in roles):
	    # if appeal_type == "Appeal for Approval":
	    #     if frappe.db.exists('Jute Mark India Registration form',{'email_id':user,'workflow_state':['in',['Approved By HO', 'Approved By RO']]}):
	    #         application_no = frappe.get_doc('Jute Mark India Registration form',{'email_id':user,'workflow_state':['in',['Approved By HO', 'Approved By RO']]}).name
	    #         return application_no
	    #     else:
	    #         frappe.throw("Your Registration Form is not in approved state")
	    #elif appeal_type == "Appeal for Rejection":
    	print("\n\n *********************************\n\n")
    	if frappe.db.exists('Jute Mark India Registration form',{'email_id':user,'workflow_state':['in',['Rejected by HO', 'Rejected by RO']]}):
    		application_no = frappe.get_doc('Jute Mark India Registration form',{'email_id':user,'workflow_state':['in',['Rejected by HO', 'Rejected by RO']]}).name
    		return application_no
    	else:
    		frappe.throw("Your Registration Form is not in Rejected state")
	    # else:
	    # 	if frappe.db.exists('Jute Mark India Registration form',{'email_id':user}):
	    # 		application_no = frappe.get_doc('Jute Mark India Registration form',{'email_id':user}).name
	    # 		return application_no
	    # 	else:
	    # 		frappe.throw(_("Registration Form is not exist for user:{0}".format(user)))
