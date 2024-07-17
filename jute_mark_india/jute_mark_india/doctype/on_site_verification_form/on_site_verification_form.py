# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt
import re
import frappe
from frappe.model.document import Document
from frappe.core.doctype.user.user import sign_up as user_signup
import os

class OnSiteVerificationForm(Document):
	def before_insert(self):
		if frappe.db.exists('On-Site Verification Form', { 'textile_registration_no': self.textile_registration_no, 'workflow_state':['not in', ['Rejected', 'Cancel By RO', 'Cancel By HO']] }):
			frappe.throw('On-Site Verification Form is already created against Application \'{0}\''.format(self.textile_registration_no))

	def validate(self):
		if (self.prev_gst_copy):
			self.validate_attachment(fieldname = self.prev_gst_copy)
		if(self.addhar_copy_from_regi):
			self.validate_attachment(fieldname = self.addhar_copy_from_regi)
		if(self.prev_udyog_aadhar_copy):
			self.validate_attachment(fieldname = self.prev_udyog_aadhar_copy)
		if(self.prev_pan_card_copy):
			self.validate_attachment(fieldname = self.prev_pan_card_copy)

		if self.no_of_labels:
			if (self.no_of_labels % 10 != 0):
				frappe.throw("no_of_labels must be multiple of 10")
			if self.no_of_labels < 50:
				frappe.throw("no_of_labels must be at least 50")

		self.set_details_from_registration_form()
		self.update_site_visit_status()

		if self.jmi_appeal and (self.workflow_state=="Approved" or self.workflow_state=="Approved By HO"):
			frappe.db.set_value("JMI Appeal", self.jmi_appeal, "workflow_state", "Approved")
			frappe.db.set_value("JMI Appeal", self.jmi_appeal, "no_of_labels", self.no_of_label_approved)
			frappe.db.commit()
		elif self.label_enhancement and (self.workflow_state=="Approved" or self.workflow_state=="Approved By HO"):
			frappe.db.set_value("Label Enhancement", self.label_enhancement, "workflow_state", "Approved")
			frappe.db.set_value("Label Enhancement", self.label_enhancement, "no_of_labels", self.no_of_label_approved)
			frappe.db.commit()
		elif self.application_renewal and (self.workflow_state=="Approved" or self.workflow_state=="Approved By HO"):
			frappe.db.set_value("Application Renewal", self.application_renewal, "workflow_state", "Approved")
			frappe.db.set_value("Application Renewal", self.application_renewal, "no_of_labels", self.no_of_label_approved)
			frappe.db.commit()


	def validate_attachment(self,fieldname):
		file_size = frappe.db.get_value('File',{'file_url':fieldname},['file_size'])
		if file_size:
			if file_size > 2000000:
				frappe.throw('File size exceeded the maximum allowed size of 2 MB')
			split_tup = os.path.splitext(fieldname)
			# extract the file name and extension
			photosite = split_tup[0]
			file_extension = split_tup[1]
			if file_extension not in ('.pdf', '.jpg', '.jpeg', '.png'):
				frappe.throw('Please Upload file format in .pdf, .jpg, .jpeg, .png')

	def set_details_from_registration_form(self):
		registration_doc = frappe.get_doc('Jute Mark India Registration form', self.textile_registration_no)
		if registration_doc.textile_details_of_product:
			self.details_of_product = []
			for row in registration_doc.textile_details_of_product:
				on_site_row = row.as_dict()
				on_site_row.pop('name')
				self.append('details_of_product', on_site_row)

		if registration_doc.textile_details_of_production_units_or_retailer_sales_outlets:
			self.textile_details_of_production_units_or_retailer_sales_outlets = []
			for row in registration_doc.textile_details_of_production_units_or_retailer_sales_outlets:
				on_site_row = row.as_dict()
				on_site_row.pop('name')
				self.append('textile_details_of_production_units_or_retailer_sales_outlets', on_site_row)

		if registration_doc.submission_of_sample_for_testing:
			self.submission_of_sample_for_testing = []
			for row in registration_doc.submission_of_sample_for_testing:
				on_site_row = row.as_dict()
				on_site_row.pop('name')
				self.append('submission_of_sample_for_testing', on_site_row)

	def update_site_visit_status(self):
		if self.site_visit_photos:
			for site_visit in self.site_visit_photos:
				frappe.db.set_value('Actual Site Visit Plan', site_visit.actual_site_visit_plan, 'site_visit_done', 1)
				frappe.db.commit()

@frappe.whitelist()
def set_label_check(app_id):
	app_doc = frappe.get_doc("Jute Mark India Registration form", app_id)
	frappe.db.set_value("Jute Mark India Registration form", app_doc.name, "label_check", 0)
	frappe.db.commit()