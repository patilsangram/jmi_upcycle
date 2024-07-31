# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import *
from frappe.model.document import Document
from jute_mark_india.jute_mark_india.utils import get_site_details
from jute_mark_india.jute_mark_india.notifications import send_notification

class ActualSiteVisitPlan(Document):
	def validate(self):
		self.validate_visiting_date()
		self.validate_km()
		if not self.assigned_for:
			self.assigned_for = frappe.session.user
			self.assigned_username = frappe.db.get_value("User", frappe.session.user, "full_name")
		site_details = get_site_details(self.application_no, self.assigned_for)
		if site_details:
			if not self.address_line1:
				self.address_line1 = site_details[0].get('site_name')
			if not self.address_visited:
				self.address_visited = site_details[0].get('site_address')

		if frappe.db.exists("On-Site Verification Form", {"textile_registration_no":self.application_no}):
			on_site_doc = frappe.get_doc("On-Site Verification Form", {"textile_registration_no":self.application_no})
			site_visit_plan = []
			for row in on_site_doc.site_visit_photos:
				site_visit_plan.append(row.actual_site_visit_plan)

			if self.name not in site_visit_plan:
				site_visit_plan = frappe.new_doc("Site Visit Photos")
				site_visit_plan.actual_site_visit_plan = self.name
				site_visit_plan.site_name = self.address_line1
				site_visit_plan.distance_in_km = self.distance_in_km
				site_visit_plan.tahsil__taluka = self.tahsil__taluka
				site_visit_plan.is_distance_150_km = self.is_distance_150_km
				site_visit_plan.unit_address = self.address_visited
				site_visit_plan.geo_location = self.visited_location
				site_visit_plan.parent = on_site_doc.name
				site_visit_plan.parentfield = "site_visit_photos"
				site_visit_plan.parenttype = "On-Site Verification Form"
				site_visit_plan.save()
				frappe.db.commit()
			else:
				frappe.db.set_value("Site Visit Photos", {"actual_site_visit_plan":self.name}, "site_name", self.address_line1)
				frappe.db.set_value("Site Visit Photos", {"actual_site_visit_plan":self.name}, "distance_in_km", self.distance_in_km)
				frappe.db.set_value("Site Visit Photos", {"actual_site_visit_plan":self.name}, "is_distance_150_km", self.is_distance_150_km)
				frappe.db.set_value("Site Visit Photos", {"actual_site_visit_plan":self.name}, "unit_address", self.address_visited)
				if self.visited_location:
					frappe.db.set_value("Site Visit Photos", {"actual_site_visit_plan":self.name}, "geo_location", self.visited_location)
				frappe.db.commit()

	def on_submit(self):
		if not self.distance_in_km:
			frappe.throw("Distance in Km should be greater than Zero!")
		if (self.assigned_for != frappe.session.user) and (frappe.session.user != 'Administrator'):
			frappe.throw("Only Assigned VO will be able to Submit the Schedule!")
		if not self.visit_planed_on:
			frappe.throw('Site Visit Plan is required!')

	def on_update_after_submit(self):
		if (self.workflow_state == 'Rejected by RO') and (not self.remarks_on_rejection):
			frappe.throw("Remarks for Rejection is Mandatory for Rejection!")
		self.validate()
		if (self.workflow_state == 'Approved By RO'):
			if self.applicant_email:
				send_notification(self.doctype, self.name, 'Site Schedule Confirmation Notification', self.applicant_email)

	def validate_km(self):
		if self.distance_in_km:
			if self.distance_in_km<0:
				frappe.throw("Distance in KM should be Greater than Zero")
			if self.distance_in_km>150:
				self.is_distance_150_km = 'Yes'
			else:
				self.is_distance_150_km = 'No'
		else:
			self.is_distance_150_km = 'No'

	def validate_visiting_date(self):
		if self.visit_planed_on:
			if getdate(self.visit_planed_on) < getdate(today()):
				frappe.throw('Please enter future date!')

	def after_insert(self):
		if self.applicant_email:
			send_notification(self.doctype, self.name, 'VO Allotment Notification', self.applicant_email)

@frappe.whitelist()
def rescheduled_site_visit(site_visit_id, rescheduled_date):
	if rescheduled_date:
		if getdate(rescheduled_date)< getdate(today()):
			frappe.throw('Please enter future date!')
		else:
			frappe.db.set_value('Actual Site Visit Plan', site_visit_id, 'visit_planed_on', rescheduled_date)
			frappe.db.set_value('Actual Site Visit Plan',site_visit_id,'workflow_state','Pending')
			frappe.db.commit()
			frappe.msgprint('Rescheduled successfully.', indicator='green', alert=True)
			doc = frappe.get_doc('Actual Site Visit Plan', site_visit_id)
			send_notification(doc.doctype, doc.name, 'Site Re-Schedule Confirmation Notification', doc.applicant_email)

@frappe.whitelist()
def get_permission_query_conditions_visit(user):
	'''
	Permission Query conditions for Actual Site Visit Plan
	'''
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	conditions = False
	if user != "Administrator":
		if "Verification Officer(VO)" in user_roles:
			conditions = '`tabActual Site Visit Plan`.`assigned_for` like "%{user}%"'.format(user = user)

		if "Regional Officer(RO)" in user_roles:
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			app_list = frappe.db.sql(""" select name from `tabJute Mark India Registration form` where regional_office = '{0}' """.format(regional_office),as_dict=1)
			#out = [item for t in app_list for item in t]
			l1 = "(" + ",".join("'{0}'".format(app.get("name")) for app in app_list) + ")"
			if len(app_list)>=1:
				conditions = '`tabActual Site Visit Plan`.`application_no` in {0}'.format(l1)
			else:
				conditions = '`tabActual Site Visit Plan`.`application_no` = "0000000"'
		if "JMI User" in user_roles:
			conditions = '`tabActual Site Visit Plan`.`application_no` = "0000000"'
		return conditions
