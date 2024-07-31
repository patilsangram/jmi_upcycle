# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
import random
from frappe.utils import *
import urllib.parse
from jute_mark_india.jute_mark_india.doctype.qr_code_settings.qr_code_settings import *
from frappe.model.document import Document

class JMIQRCode(Document):
	def before_insert(self):
		self.set_prerequisites()

	def after_insert(self):
		self.add_checksum_number()
		self.encrypt_qrcode_id()
		self.create_jmi_url()
		self.generate_qr_code_for_id()
		self.save()

	def set_prerequisites(self):
		'''Method to set pre requisites to generate QR Code ID'''
		creation_month = getdate(today()).month

		#Creating Production Month
		if creation_month <= 10:
			self.production_month = '0' + str(creation_month)
		else:
			self.production_month = str(creation_month)

		#Creating Production Year
		self.production_year = str(getdate(today()).year)

		self.qrcode_id = self.production_month + self.production_year + self.sequence_number

		#Create and add checksum number
		self.checksum_number = self.generate_checksum_number()

	def generate_checksum_number(self):
		''' Method to generate Check Sum Number based on ID Generated '''
		if(self.qrcode_id):
			checksum, idx, checksum_number = 0, 0, 0
			str_qrcode_id = self.qrcode_id
			for id in str_qrcode_id:
				checksum += (idx*int(id))
				idx += 1
			qr_constant = frappe.db.get_single_value('QR Code Settings', 'qr_code_generation_constant')
			if not qr_constant:
				frappe.throw(title='Configuration Missing', msg='Please set QR Code Generation Constant in QR Code Settings')
			checksum_number = checksum % qr_constant
			return checksum_number

	def add_checksum_number(self):
		''' Method to update qrcode_id with checksum number '''
		if(self.checksum_number and self.qrcode_id):
			self.qrcode_id = self.qrcode_id + str(self.checksum_number)
		elif self.qrcode_id:
			self.qrcode_id = self.qrcode_id + '0'

	def encrypt_qrcode_id(self):
		''' Method to encrypt QRCode ID '''
		self.encrypted_qrcode_id = encrypt_msg(self.qrcode_id)

	def create_jmi_url(self):
		''' Method to create JMI Url to display product details '''
		jmi_url = frappe.utils.get_url()
		jmi_url += '/qr-code/' + self.encrypted_qrcode_id
		self.jmi_url = jmi_url

	def generate_qr_code_for_id(self):
		''' Method to Create QR Codes with ID '''
		if(self.jmi_url):
			chart = "https://chart.googleapis.com/chart?chs=100x100&cht=qr&choe=UTF-8&chl="
			chart_url = chart + urllib.parse.quote_plus(self.jmi_url)
			img_tag = "<img src='"+chart_url+"'>"
			self.qr_code_link = chart_url
			self.qr_code = img_tag

@frappe.whitelist()
def get_permission_query_conditions_jmi_qr(user):
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
			conditions = '`tabJMI QR Code`.`allocated_to` like "%{regional_office}%" '.format(regional_office = regional_office)
		elif 'JMI User' in user_roles:
			conditions = '`tabJMI QR Code`.`allocated_to_user` like  "%{user}%" '.format(user = user)

		return conditions
