# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
import pyotp
import re
from frappe.model.document import Document
from frappe.utils import validate_phone_number
from frappe import _
from frappe.core.doctype.user.user import sign_up as user_signup
import frappe.utils.data as data
import os
from frappe.model.naming import make_autoname
import frappe.model.rename_doc as rd
from jute_mark_india.jute_mark_india.utils import *
from frappe.utils import add_days, add_months, add_years, cstr, getdate, today
from jute_mark_india.jute_mark_india.notifications import send_notification

class JuteMarkIndiaRegistrationform(Document):
	def onload(self):
		self.calculate_progress()

	@frappe.whitelist()
	def get_amount(self):
		amount = 0
		fees_list = frappe.get_list("Fees Records", filters={"fees_description": "New Registration", "category": self.category_b})
		if fees_list:
			for i in fees_list:
				amount = frappe.get_value("Fees Records", i.name, "amount" ) 
		return amount
	
	def before_save(self):
		self.set_category_id()
		if self.njb_regi_no:
			if not validate_njb_number(self.njb_regi_no):
				frappe.throw("Invalid NJB Registration Number ")
		if self.udyog_aadhar:
			if not validate_udayam_adhar(self.udyog_aadhar):
				frappe.throw('Invalid Udayam Aadhar')
		# if self.udyog_aadhar:
		# 	if not check_udyog_aadhar(self.udyog_aadhar):
		# 		frappe.throw('Is already Exists')

		if self.address_line_1:
			if not re.match(r'^[A-Za-z0-9\s.,_()&-]+$',self.address_line_1):
				frappe.throw("Invalid address line 1")

		if self.email_id:
			regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
			if(not(re.fullmatch(regex, self.email_id))):
				frappe.throw("Invalid Email")

		if self.pan_number:
			regex = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
			if(not(re.fullmatch(regex, self.pan_number))):
				frappe.throw("Invalid PAN Number ")

		if self.gst_number:
			regex = '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
			if(not(re.fullmatch(regex, self.gst_number))):
				frappe.throw("Invalid GST Number ")

		if self.aadhar_number:
			if len(str(self.aadhar_number))!=12:
				frappe.throw(frappe._("Please enter 12 digit Aadhar Number"))
				aadhar_number = str(self.aadhar_number)
				self.validate_aadhar_number()

		if len(str(self.mobile_number))!=10 :
			frappe.throw(frappe._("Please enter 10 digit mobile number"))

		if self.mobile_number:
			number = self.mobile_number
			pattern = r'^(\+91[\-\s]?)?[6789]\d{9}$'
			match = re.match(pattern, number)
			if bool(match)==False:
				frappe.throw("Invalid Mobile Number!!")
			else:
				return bool(match)
			return bool(match)

	def set_category_id(self):
		if self.category_b:
			if self.category_b == 'Artisan':
				self.category_id = 1
			if self.category_b == 'Manufacturer':
				self.category_id = 2
			if self.category_b == 'Retailer':
				self.category_id = 3

	def autoname(self):
		self.set_category_id()
		self.name = make_autoname('A-' + str(self.district_code) + '-' + str(self.category_id)+ '-' + '.####.')
		self.registration_number = self.name

	def after_insert(self):
		self.create_user_if_not_exists()
		self.registration_number = self.name

	def create_user_if_not_exists(self):
		if self.email_id and not frappe.db.exists('User', self.email_id):
			default_role = frappe.db.get_single_value('Android App Settings', 'default_role_on_signup')
			user_doc = frappe.new_doc('User')
			user_doc.first_name = self.applicant_name
			user_doc.email = self.email_id
			user_doc.mobile_no = self.mobile_number
			if  default_role:
				user_role = user_doc.append('roles')
				user_role.role = default_role
			user_doc.save(ignore_permissions=True)
			frappe.db.commit()

	def validate(self):
		self.update_details_of_production()
		self.update_enhanced_labels()
		if self.state and self.district:
			regional_office = get_regional_office(self.state, self.district)
			if regional_office:
				self.regional_office = regional_office
		if(self.workflow_state == "Assigned VO"):
			self.set_site_details_for_artsian()
			self.validate_vo_assignment()
			self.assign_sites()
			create_on_site_verification_from_registration(self.name)
			frappe.db.commit()
		self.set_category_id()
		if self.photo:
			self.validate_attachment(fieldname = self.photo)
		if self.proof_of_address:
			self.validate_attachment(fieldname = self.proof_of_address)
		if self.gst_copy:
			self.validate_attachment(fieldname = self.gst_copy)
		if self.certificate_of_registration__in_case_b_is_2_or_3:
			self.validate_attachment(fieldname = self.certificate_of_registration__in_case_b_is_2_or_3)
		if self.identification_proof_is:
			self.validate_attachment(fieldname = self.identification_proof_is)
		if self.identification_proof:
			self.validate_attachment(fieldname = self.identification_proof)
		if self.aadhar_card_copy:
			self.validate_attachment(fieldname = self.aadhar_card_copy)
		if self.udyog_aadhar_copy:
			self.validate_attachment(fieldname = self.udyog_aadhar_copy)
		if self.pan_card_copy:
			self.validate_attachment(fieldname = self.pan_card_copy)
		if self.upload_agreement:
			self.validate_agreement_attachment()

		if(self.workflow_state == "Draft"):
			send_notification(self.doctype, self.name, 'Incomplete Application Notification', self.email_id)

		if(self.workflow_state == "Application Submitted"):
			user_role = frappe.get_roles(frappe.session.user)
			if not self.is_paid and "JMI User" in user_role:
				frappe.throw("Please Proceed Payment First !")
				
			if self.category_b != 'Artisan':
				if not is_site_details_filled(self.name):
					frappe.throw("Please fill Site Details")
			if(not self.i_agree):
				frappe.throw("Please check <b>I Agree</b> button")
			self.validate_details_of_product()
			self.add_document_rows()
			send_notification(self.doctype, self.name, 'Application Submitted Notification', self.email_id)

		if(self.workflow_state == "Assigned VO"):
			assigned_to = frappe.db.get_value('Jute Mark India Registration form', {'name':self.name}, ['_assign'])
			if(not assigned_to):
				frappe.throw("Please Assign VO")


		if self.textile_details_of_production_units_or_retailer_sales_outlets:
			for row in self.textile_details_of_production_units_or_retailer_sales_outlets:
				if row.approve == 1:
					self.details_of_production_in_previous_year_section = 1
					break

		self.validate_on_site_verification()
		self.validate_on_mandetory_fields()
		if self.workflow_state in ['Approved By RO', 'Approved By HO']:
			if self.registration_number[0] == 'A':
				registration_number = create_reg_no(self.name)
				self.registration_number = registration_number
				frappe.db.set_value(self.doctype, self.name, 'registration_number', registration_number)
				self.set_registration_and_renewal_date()
				if not frappe.db.exists('JMI Registration', {"application_number": self.name}):
					jmi_reg = frappe.new_doc('JMI Registration')
					jmi_reg.application_number = self.name
					jmi_reg.ro_user_id = frappe.session.user
					jmi_reg.submit()
					frappe.db.commit()
				send_notification(self.doctype, self.name, 'Registration Completed Notification', self.email_id)

		if self.workflow_state in ['Approval Pending By RO', 'Approval Pending By HO']:
			for production_unit in self.textile_details_of_production_units_or_retailer_sales_outlets:
				if production_unit.site_visit_id:
					send_notification('Actual Site Visit Plan', production_unit.site_visit_id, 'Verification Completed Notification', self.email_id)

	def validate_attachment(self, fieldname):
		file_size =frappe.db.get_value('File',{'file_url':fieldname},['file_size'])
		file_name =frappe.db.get_value('File',{'file_url':fieldname},['attached_to_field'])
		if file_size:
			if file_size > 2000000:
				frappe.throw(f'File size of {file_name} exceeded the maximum allowed size of 2 MB')
			file_size = ' '
			split_tup = os.path.splitext(fieldname)
			photosite = split_tup[0]
			file_extension = split_tup[1]
			if file_extension not in ('.pdf', '.jpg', '.jpeg', '.png'):
				frappe.throw(f'Please Upload {file_name} file format in .pdf, .jpg, .jpeg, .png')

	def validate_agreement_attachment(self):
		if self.upload_agreement:
			file_size =frappe.db.get_value('File',{'file_url': self.upload_agreement },['file_size'])
			file_name =frappe.db.get_value('File',{'file_url': self.upload_agreement },['attached_to_field'])
			if file_size:
				if file_size > 5320000:
					frappe.throw(f'File size of {file_name} exceeded the maximum allowed size of 5 MB')
				split_tup = os.path.splitext(self.upload_agreement)
				photosite = split_tup[0]
				file_extension = split_tup[1]
				if file_extension != '.pdf':
					frappe.throw(f'Please Upload Agreement file format in .pdf')

	def validate_name(self):
		pattern = r'^[A-Za-z\s.]*$'
		match = re.match(pattern, self.applicant_name)
		if bool(match)==False:
			frappe.throw("Please Enter First Name In Letters Only..")
		else:
			return bool(match)

	def calculate_progress(self):
		no_of_fields = list(frappe.db.describe('Jute Mark India Registration form'))
		actual_fields = [i[0] for i in no_of_fields][7:-6:]
		progress = 0
		weitage = 100/(len(actual_fields))
		for field in actual_fields:
			value = frappe.db.get_value(self.doctype,self.name,field)
			if value:
				progress += weitage
		self.progress=progress

	def validate_aadhar_number(self):
		if len(str(self.aadhar_number)) != 12 :
			frappe.throw("Please Enter 12 digit Aadhaar Number !!")
		if not str(self.aadhar_number).isdigit():
			frappe.throw("Invalid Aadhaar Number!! Avoid alphabets..")
		factors = [int(x) * (2 - i % 2) for i, x in enumerate(str(self.aadhar_number))]
		total = sum([sum(divmod(factor, 10)) for factor in factors])
		return total % 10 == 0

	def validate_on_site_verification(self):
		if self.workflow_state == 'Submitted':
			site_visit_details = get_primary_site_details(self.name)
			if not site_visit_details:
				frappe.throw('No Primary Site found!')
			else:
				if site_visit_details.assigned_for != frappe.session.user:
					frappe.throw('Only VOs allocated to the primary site can submit the application to RO!')
				if site_visit_details.workflow_state != 'Approved By RO':
					frappe.throw('Actual Site Visit Plan is not yet Approved for Primary Site!')

		if self.workflow_state in ['Approved By HO', 'Approved By RO']:
			if frappe.db.exists('Actual Site Visit Plan', { 'application_no':self.name }):
				site_visits = frappe.db.get_all('Actual Site Visit Plan', { 'application_no':self.name})
				for site in site_visits:
					site_visit_doc = frappe.get_doc('Actual Site Visit Plan', site.name)
					if not site_visit_doc.site_visit_done:
						frappe.throw('Site visit not yet done for Site Visit id : {0}'.format(site.name))

	def validate_on_mandetory_fields(self):
		if self.workflow_state == 'Submitted':
			if not self.tahsil__taluka:
				frappe.throw("Please add Tahsil/Taluka!")
			if not self.townvillage:
				frappe.throw("Please add Town/Village!")

			if self.category_b == 'Artisan':
				if not self.religion:
					frappe.throw("Please add Religion!")
				if not self.category__scst_other_in_case_b_is_1:
					frappe.throw("Please add Category!")
				if not self.aadhar_number:
					frappe.throw("Please add Aadhar Number!")
				if not self.aadhar_card_copy:
					frappe.throw("Please attach Aadhar Copy!")
				if not self.identification_proof:
					frappe.throw("Please add Identification_proof!")
			else:
				if not self.gst_number:
					frappe.throw("please add GST Number!")
				if not self.gst_copy:
					frappe.throw("Please attach GST Copy!")
				if not self.pan_number:
					frappe.throw("Please add Pan Number!")
				if not self.pan_card_copy:
					frappe.throw("Please attach PAN card Copy!")
				if not self.udyog_aadhar:
					frappe.throw("Please add Udyog Aadhar Number!")
				if not self.udyog_aadhar_copy:
					frappe.throw("Please attach Udyog Aadhar copy!")
				if not self.certificate_of_registration__in_case_b_is_2_or_3:
					frappe.throw("Please attach certificate_of_registration!")

			if not self.photo:
				frappe.throw("Please add Passport size photo!")
			if not  self.proof_of_address:
				frappe.throw("Please add Proof of Address!")
			if not self.upload_agreement:
				frappe.throw("Please Upload Agreement!")
			for row in self.documents:
				if not row.upload_test_report:
					frappe.throw("Please Upload Test Report in Documents Section")


			if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':self.name}):
				on_site_doc = frappe.get_doc("On-Site Verification Form",{'textile_registration_no':self.name})
				#check_for_on_site_req(self.name)
				if not on_site_doc.no_of_labels:
					frappe.throw(_("Please add No of Lables on On-Site Verification Form : {0}".format(on_site_doc.name)))
				if not on_site_doc.signature_with_name:
					frappe.throw(_("Please add Signature on On-Site Verification Form : {0}".format(on_site_doc.name)))

				for row in on_site_doc.site_visit_photos:
					if not row.photograph_1:
						frappe.throw(_("Please add Site Photographs in Site visit photograph  of On-Site Verification Form : {0} and Actual Site Visit:{1}".format(on_site_doc.name,row.actual_site_visit_plan)))
				# need to give message for no. of approved labels
				if on_site_doc.label_enhancement and on_site_doc.no_of_label_approved == 0:
					frappe.throw(_("Please add No. of Label Approved on On-Site Verification Form : {0}".format(on_site_doc.name)))


	def assign_sites(self):
		assign_count = 0
		for row in self.textile_details_of_production_units_or_retailer_sales_outlets:
			''' To Assign Sites from Child Table '''
			if row.assign_to:
				assign_count += 1
				if assign_count == 1:
					self.assign_to = row.assign_to
				desc = "Assigned site - Address : " + row.name_of_unit__outlet + ", " + row.address
				if not frappe.db.exists("Actual Site Visit Plan",{"application_no":self.name,"address_line1":row.name_of_unit__outlet,"no_of_male_artisan":row.no_of_male_artisan,"no_of_female_artisan":row.no_of_female_artisan,"no_of_other_artisan":row.no_of_other_artisan}):
					if not frappe.db.exists("ToDo", { "allocated_to": row.assign_to, "reference_type":self.doctype, "reference_name":self.name, "description":desc }):
						create_todo(row.assign_to, desc, self.doctype, self.name)
						if assign_count == 1:
							site_visit_id = schedule_site_visit(self.name, row.name_of_unit__outlet, row.assign_to, row.address, row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan, 1)
						else:
							site_visit_id = schedule_site_visit(self.name, row.name_of_unit__outlet, row.assign_to, row.address, row.no_of_male_artisan, row.no_of_female_artisan, row.no_of_other_artisan)
						row.site_visit_id = site_visit_id
				else:
					site_doc = frappe.get_doc("Actual Site Visit Plan",{"application_no":self.name,"address_line1":row.name_of_unit__outlet,"no_of_male_artisan":row.no_of_male_artisan,"no_of_female_artisan":row.no_of_female_artisan,"no_of_other_artisan":row.no_of_other_artisan})
					if site_doc.assigned_for != row.assign_to:
						full_name = frappe.db.get_value("User", row.assign_to, "full_name")
						frappe.db.set_value("Actual Site Visit Plan", site_doc.name, "assigned_for", row.assign_to)
						frappe.db.set_value("Actual Site Visit Plan", site_doc.name, "assigned_username", full_name)
						if site_doc.workflow_state == "Approved By RO" or site_doc.workflow_state == "Pending":
							frappe.db.set_value("Actual Site Visit Plan", site_doc.name, "workflow_state", "Draft")
							frappe.db.set_value("Actual Site Visit Plan", site_doc.name, "distance_in_km", 0)
							frappe.db.set_value("Actual Site Visit Plan", site_doc.name , "visit_planed_on", "")
						frappe.db.commit()


	def update_enhanced_labels(self):
		if self.workflow_state == "Approved By RO":
			if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':self.name}):
				on_site_doc = frappe.get_doc("On-Site Verification Form",{'textile_registration_no':self.name})
				if on_site_doc.label_enhancement:
					enhance_doc =  frappe.get_doc("Label Enhancement",on_site_doc.label_enhancement)
					if enhance_doc.workflow_state == "Assigned VO":
						frappe.db.set_value("Label Enhancement",enhance_doc.name,'workflow_state',"Approved")
						frappe.db.set_value('On-Site Verification Form', on_site_doc.name, 'no_of_labels', on_site_doc.no_of_label_approved)
						self.application_label_enhancement = 0
						frappe.db.commit()
						for en_row in enhance_doc.assign_vo_for_sites:
							flag = 0
							for row in self.textile_details_of_production_units_or_retailer_sales_outlets:
								if en_row.name_of_unit__outlet == row.name_of_unit__outlet:
									flag = 1
									row.address = en_row.address
									row.no_of_male_artisan = en_row.no_of_male_artisan
									row.no_of_female_artisan = en_row.no_of_female_artisan
									row.no_of_other_artisan = en_row.no_of_other_artisan
							if flag == 0:
								row = self.append('textile_details_of_production_units_or_retailer_sales_outlets')
								row.name_of_unit__outlet = en_row.name_of_unit__outlet
								row.address = en_row.address
								row.no_of_male_artisan = en_row.no_of_male_artisan
								row.no_of_female_artisan = en_row.no_of_female_artisan
								row.no_of_other_artisan = en_row.no_of_other_artisan
						frappe.db.commit()
				if on_site_doc.jmi_appeal:
					appeal_doc = frappe.get_doc("JMI Appeal",on_site_doc.jmi_appeal)
					if appeal_doc.workflow_state == "Assigned VO":
						frappe.db.set_value("JMI Appeal",appeal_doc.name,'workflow_state',"Approved")
						frappe.db.commit()
						for en_row in appeal_doc.assign_vo_for_sites:
							flag = 0
							for row in self.textile_details_of_production_units_or_retailer_sales_outlets:
								if en_row.name_of_unit__outlet == row.name_of_unit__outlet:
									flag = 1
									row.address = en_row.address
									row.no_of_male_artisan = en_row.no_of_male_artisan
									row.no_of_female_artisan = en_row.no_of_female_artisan
									row.no_of_other_artisan = en_row.no_of_other_artisan
							if flag == 0:
								row = self.append('textile_details_of_production_units_or_retailer_sales_outlets')
								row.name_of_unit__outlet = en_row.name_of_unit__outlet
								row.address = en_row.address
								row.no_of_male_artisan = en_row.no_of_male_artisan
								row.no_of_female_artisan = en_row.no_of_female_artisan
								row.no_of_other_artisan = en_row.no_of_other_artisan
						frappe.db.commit()

				if on_site_doc.application_renewal:
					renew_doc = frappe.get_doc("Application Renewal",on_site_doc.application_renewal)
					if renew_doc.workflow_state == "Assigned VO":
						frappe.db.set_value("Application Renewal",renew_doc.name,'workflow_state',"Approved")
						frappe.db.commit()
						update_renewal_dates(self.name)
						send_notification(self.doctype, self.name, 'Renewal Complete Notification', self.email_id)
						for en_row in renew_doc.assign_vo_for_sites:
							flag = 0
							for row in self.textile_details_of_production_units_or_retailer_sales_outlets:
								if en_row.name_of_unit__outlet == row.name_of_unit__outlet:
									flag = 1
									row.address = en_row.address
									row.no_of_male_artisan = en_row.no_of_male_artisan
									row.no_of_female_artisan = en_row.no_of_female_artisan
									row.no_of_other_artisan = en_row.no_of_other_artisan
							if flag == 0:
								row = self.append('textile_details_of_production_units_or_retailer_sales_outlets')
								row.name_of_unit__outlet = en_row.name_of_unit__outlet
								row.address = en_row.address
								row.no_of_male_artisan = en_row.no_of_male_artisan
								row.no_of_female_artisan = en_row.no_of_female_artisan
								row.no_of_other_artisan = en_row.no_of_other_artisan
						frappe.db.commit()

		if self.workflow_state == "Rejected by RO":
			if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':self.name}):
				on_site_doc = frappe.get_doc("On-Site Verification Form",{'textile_registration_no':self.name})
				if on_site_doc.label_enhancement:
					enhance_doc =  frappe.get_doc("Label Enhancement",on_site_doc.label_enhancement).name
					frappe.db.set_value("Label Enhancement",enhance_doc,'workflow_state',"Rejected")
					self.application_label_enhancement = 0
					frappe.db.commit()
				elif on_site_doc.jmi_appeal:
					appeal_doc = frappe.get_doc("JMI Appeal",on_site_doc.jmi_appeal)
					if appeal_doc.workflow_state == "Assigned VO":
						frappe.db.set_value("JMI Appeal",appeal_doc.name,'workflow_state',"Rejected")
						frappe.db.commit()
				elif on_site_doc.application_renewal:
					renew_doc = frappe.get_doc("Application Renewal",on_site_doc.application_renewal)
					if renew_doc.workflow_state == "Assigned VO":
						frappe.db.set_value("Application Renewal",renew_doc.name,'workflow_state',"Rejected")
						frappe.db.commit()

	@frappe.whitelist()
	def validate_details_of_product(self):
		if not self.textile_details_of_product:
			frappe.throw('Textile details of Product is required!')
		if is_sampling_required(self.name):
			if not (self.attach_sample_report or self.submission_of_sample_for_testing):
				frappe.throw("Either you need to enable \'<b>Will You Submit Sample Report</b>\' checkbox or \'<b>Submission of Sample For Testing</b>\' Table need to be filled!")

	def add_document_rows(self):
		rows_added = False
		if self.textile_details_of_product:
			for textile_details in self.textile_details_of_product:
				if textile_details.test_report_details == 'Not Available' and not textile_details.document_row_added:
					row = self.append('documents')
					row.product_type = textile_details.product_type
					row.product_description = textile_details.product_description
					row.jmi_product_function = textile_details.function_of_jute_material_in_the_product
					textile_details.document_row_added = 1
					rows_added = True
		if rows_added:
			send_notification(self.doctype, self.name, 'Sample Submission Notification', self.email_id)

	def set_site_details_for_artsian(self):
		if self.category_b == 'Artisan':
			no_of_male_artisan, no_of_female_artisan, no_of_other_artisan = 0, 0, 0
			if self.gender:
				if self.gender == 'Male':
					no_of_male_artisan = 1
				if self.gender == 'Female':
					no_of_female_artisan = 1
				if self.gender == 'Other':
					no_of_other_artisan = 1
			address = self.address_line_1
			if self.address_line_2:
				address += ', {0}'.format(self.address_line_2)
			if self.address_line_3:
				address += ', {0}'.format(self.address_line_3)
			if not self.textile_details_of_production_units_or_retailer_sales_outlets:
				row = self.append('textile_details_of_production_units_or_retailer_sales_outlets')
				row.name_of_unit__outlet = self.address_line_1
				row.address = address
				row.no_of_male_artisan = no_of_male_artisan
				row.no_of_female_artisan = no_of_female_artisan
				row.no_of_other_artisan = no_of_other_artisan
				if self.assign_to:
					row.assign_to = self.assign_to

	@frappe.whitelist()
	def save_next(self):
		self.ignore_mandatory = True
		self.save()
		frappe.db.commit()

	@frappe.whitelist()
	def save_submit(self):
		self.workflow_state = 'Application Submitted'
		self.save()
		frappe.db.commit()

	@frappe.whitelist()
	def validate_vo_assignment(self):
		vo_assignment_count = 0
		for row in self.textile_details_of_production_units_or_retailer_sales_outlets:
			if row.assign_to:
				vo_assignment_count += 1
		if vo_assignment_count == 0:
			frappe.throw('Atleast one site should Assign to VO!')

	def update_details_of_production(self):
		if self.textile_details_of_product:
			for textile_details in self.textile_details_of_product:
				if not textile_details.previous_year_row_added:
					#submission_of_sample_for_testing
					exists = False
					for row in self.submission_of_sample_for_testing:
						if row.product_type == textile_details.product_type and row.description_of_product == textile_details.product_description and row.function_of_jute_material_in_the_product == textile_details.function_of_jute_material_in_the_product:
							exists = True
							break
					if not exists:
						if textile_details.test_report_details == 'Not Available':
							row = self.append('submission_of_sample_for_testing')
							row.product_type = textile_details.product_type
							row.description_of_product = textile_details.product_description
							row.function_of_jute_material_in_the_product = textile_details.function_of_jute_material_in_the_product
							row.declared_fibre_content = textile_details.fiber_content
				textile_details.previous_year_row_added = 1

	def set_registration_and_renewal_date(self):
		if not self.registration_date:
			self.registration_date = getdate(today())
		registration_date = self.registration_date
		if frappe.db.get_single_value("JMI Settings", "application_renewal_year"):
			application_renewal_in_years = frappe.db.get_single_value("JMI Settings", "application_renewal_year")
			renewal_date = add_days(getdate(registration_date), application_renewal_in_years)
			self.next_renewal_date = renewal_date

@frappe.whitelist()
def get_permission_query_conditions(user):
	'''
	Permission Query conditions for Jute Mark India Reg Form
	'''
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	conditions = False
	if user != "Administrator":
		if not ('HO' in user_roles or 'Regional Officer(RO)' in user_roles):
			conditions = '`tabJute Mark India Registration form`.`_assign` like "%{user}%" or `tabJute Mark India Registration form`.`owner` like "%{user}%"'.format(user = user)
		if 'JMI User' in user_roles:
			conditions = '`tabJute Mark India Registration form`.`owner` like "%{user}%" or `tabJute Mark India Registration form`.`email_id` like "%{user}%"'.format(user = user)
		if 'Regional Officer(RO)' in user_roles:
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			# conditions = '`tabJute Mark India Registration form`.`regional_office` like "%{regional_office}%" '.format(regional_office = regional_office)
			conditions = '`tabJute Mark India Registration form`.`regional_office` like "%{regional_office}%" and `tabJute Mark India Registration form`.`workflow_state` in  ("Application Submitted","Approval Pending By RO","Approved By RO","Rejected by RO","Re-Assign","Assigned VO")'.format(regional_office = regional_office)
		return conditions

@frappe.whitelist()
def get_site_visit_status(application_no):
	''' Method to get sum of Task Score in Tasks by Project'''
	status = False
	query = """
		SELECT
			workflow_state
		FROM
			`tabActual Site Visit Plan`
		WHERE
			application_no = %(application_no)s
		ORDER BY
			creation DESC
	"""
	doc_list = frappe.db.sql(query.format(),{ 'application_no' : application_no }, as_dict = 1)
	if doc_list:
		if doc_list[0].workflow_state:
			status = doc_list[0].workflow_state
	return status

#showing vo which is under that perticular RO Office
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def set_assign_to(doctype, txt, searchfield, start, page_len, filters):
	user = frappe.session.user
	roles = frappe.get_roles(user)
	if not frappe.session.user == "Administrator":
		if 'Regional Officer(RO)' in roles:
			reg_office = frappe.db.get_value("User wise RO",user,'regional_office')
			if reg_office:
				return frappe.db.sql("""select u.name from `tabUser` u join `tabHas Role` h on u.name = h.parent where h.role='Verification Officer(VO)' and h.parenttype="User" and u.name in (select name from `tabUser wise VO` where regional_office='{}') """.format(reg_office))
			else:
				frappe.throw(_("Please add Regional Office for User : {} in Doctype User wise RO"))
	else:
		return frappe.db.sql(""" select u.name from `tabUser` u join `tabHas Role` h on u.name = h.parent where h.role='Verification Officer(VO)' and h.parenttype='User';""")

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_package_unit(doctype, txt, searchfield, start, page_len, filters):
	cond = ""
	if filters and filters.get("product_type"):
		cond = "and parent = '%s'" % filters.get("product_type")

	return frappe.db.sql(
		"""select name from `tabJMI UOM`
			where `{key}` LIKE %(txt)s
			and name in (select jmi_uom from `tabProduct Type UOM` where 1=1 {cond})
			order by name limit %(page_len)s offset %(start)s""".format(
			key=searchfield, cond=cond
		),
		{"txt": "%" + txt + "%", "start": start, "page_len": page_len},
	)


@frappe.whitelist()
def create_reg_no(application_no):
	'''
		Method to create Registration Number
	'''
	registration_no = False
	if application_no:
		registration_no = application_no.replace("A", "R")
	return registration_no

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def regional_office_filter_query(doctype, txt, searchfield, start, page_len, filters):
	if filters:
		query = """
			select
				distinct ro.name
			from
				`tabRegional Office` as ro,
				`tabStates` as s,
				`tabDistricts` as d
			where
				ro.name = s.parent AND
				ro.name = d.parent
		"""
		if filters.get('state'):
			query+= "AND s.state = '{state}'".format(state=filters['state'])
		if filters.get('district'):
			query+= "AND d.district = '{district}'".format(district=filters['district'])
	else:
		query = """
			select
				name
			from
				`tabRegional Office`
		"""
	return frappe.db.sql(query)

@frappe.whitelist()
def create_on_site_verification_from_registration(application_no):
	'''
		Method to Create On-Site Verification form from JMI Registration
	'''
	if frappe.db.exists('Jute Mark India Registration form', application_no):
		if not frappe.db.exists('On-Site Verification Form', { 'textile_registration_no': application_no }):
			on_site_verification = frappe.new_doc('On-Site Verification Form')
			on_site_verification.textile_registration_no = application_no
			on_site_verification.flags.ignore_mandatory = True
			on_site_verification.save(ignore_permissions=True)
			frappe.db.commit()

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def jmi_uom_query(doctype, txt, searchfield, start, page_len, filters):
	if filters.get('product_type'):
		query = """
			SELECT
				jmi_uom
			FROM
				`tabProduct Type UOM`
			WHERE
				parent = "{product_type}" AND
				jmi_uom like "{txt}"
		""".format(product_type=filters['product_type'], txt='%'+txt+'%')
		return frappe.db.sql(query)
	else:
		return []

# @frappe.whitelist()
# def jmi_application_renew():
# 	jmi_app = frappe.db.sql("""SELECT name, date as application_date FROM `tabJute Mark India Registration form` where application_renewal=0 and workflow_state in ('Approved By RO', 'Approved By HO', 'Approval Pending By RO') """, as_dict=1)
# 	years = frappe.db.get_single_value("JMI Settings", "application_renewal_year")
# 	months = (years*12)-1
# 	for row in jmi_app:
# 		renewal_date = add_months(getdate(row.get("application_date")), months)
# 		if getdate(renewal_date)==getdate(today()):
# 			frappe.db.set_value("Jute Mark India Registration form", row.get("name"), "application_renewal", 1)
# 			frappe.db.commit()

@frappe.whitelist()
def jmi_application_renew():
	curent_date = getdate(today())
	renew_date = getdate(add_months(curent_date, 1))
	jmi_applications = frappe.db.get_all('Jute Mark India Registration form', { 'application_renewal':0, 'workflow_state': ['in', ['Approved By RO', 'Approved By HO', 'Approval Pending By RO']], 'next_renewal_date': ['<=', renew_date ] })
	for jmi_application in jmi_applications:
		frappe.db.set_value("Jute Mark India Registration form", jmi_application.name, "application_renewal", 1)
		frappe.db.commit()

@frappe.whitelist()
def check_for_on_site_req(app_name):
	user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if 'Verification Officer(VO)' in user_roles and user != "Administrator":
		flag = 0
		if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':app_name}):
			on_site_doc = frappe.get_doc("On-Site Verification Form",{'textile_registration_no':app_name})
			# need to check all pending -- sites must be approbved by RO -- not single
			visit_plan_list = frappe.get_list("Actual Site Visit Plan",{'application_no':app_name})
			flag = 0
			for visit in visit_plan_list:
				state = frappe.get_doc("Actual Site Visit Plan",visit).workflow_state
				if state != "Approved By RO":
					flag = 1
					break
			#if frappe.db.exists("Actual Site Visit Plan",{'application_no':app_name,'workflow_state':"Approved By RO"}):
			if flag == 0:
				if not on_site_doc.no_of_labels:
					frappe.throw(_("Please add No of Lables on On-Site Verification Form : {0}".format(on_site_doc.name)))
				if not on_site_doc.signature_with_name:
					frappe.throw(_("Please add Signature on On-Site Verification Form : {0}".format(on_site_doc.name)))

				for row in on_site_doc.site_visit_photos:
					if not row.photograph_1:
						frappe.throw(_("Please add Site Photographs in Site visit photograph  of On-Site Verification Form : {0} and Actual Site Visit:{1}".format(on_site_doc.name,row.actual_site_visit_plan)))
				# need to give message for no. of approved labels
				if on_site_doc.label_enhancement and on_site_doc.no_of_label_approved == 0:
					frappe.throw(_("Please add No. of Label Approved on On-Site Verification Form : {0}".format(on_site_doc.name)))

def update_renewal_dates(jmi_application_no):
	if frappe.db.get_single_value("JMI Settings", "application_renewal_year"):
		application_renewal_in_years = frappe.db.get_single_value("JMI Settings", "application_renewal_year")
		next_renewal_date = add_days(getdate(today()), application_renewal_in_years)
		frappe.db.set_value('Jute Mark India Registration form', jmi_application_no, 'renewed_on', getdate(today()))
		frappe.db.set_value('Jute Mark India Registration form', jmi_application_no, 'next_renewal_date', getdate(next_renewal_date))
		frappe.db.commit()
