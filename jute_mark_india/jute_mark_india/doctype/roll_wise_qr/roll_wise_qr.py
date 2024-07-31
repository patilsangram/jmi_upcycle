# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class RollwiseQR(Document):
	#setting available quantity and status
	def validate(self):
		from_seq = frappe.db.get_value("JMI QR Code",self.available_from_qr_code,'sequence_number')
		end_seq = frappe.db.get_value("JMI QR Code",self.available_end_qr_code,'sequence_number')
		qty = int(end_seq) - int(from_seq)
		self.no_of_labels = qty + 1
		if self.status!="Allocated":
			self.available_qantity = qty + 1
		
		

@frappe.whitelist()
def get_permission_query_conditions_roll(user):
	'''
	Permission Query conditions for JMI QR Code for Perticular RO
	'''
	if not user:
		user = frappe.session.user
	user_roles = frappe.get_roles(user)
	conditions = False
	if user != "Administrator":
		if 'Regional Officer(RO)' in user_roles:
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			conditions = '`tabRoll wise QR`.`allocated_to` like "%{regional_office}%" '.format(regional_office = regional_office)
		return conditions