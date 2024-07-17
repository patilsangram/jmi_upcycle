# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import *
from frappe.model.document import Document

class JMIQRCodeBuilder(Document):
	def validate(self):
		if self.qty:
			if self.qty<10 or self.qty > 100000:
				frappe.throw('Qty should be in range of 10 - 100000')
			else:
				if self.qty%10 :
					frappe.throw('Qty should be in multiple of 10')
	def before_save(self):
		self.set_prerequisites()

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

	@frappe.whitelist()
	def generate_qr_codes(self):
		if not self.qty:
			frappe.throw(title='Qty is Missing!', msg='Please set Qty.')
		frappe.db.set_value('JMI QR Code Builder', self.name, 'status', 'Started')
		frappe.db.commit()
		self.reload()
		frappe.enqueue(create_qr_codes_in_background, doc=self, queue="long")

@frappe.whitelist()
def create_qr_codes_in_background(doc):
	try:
		if doc.qty:
			r_num = 0
			for count in range(0, doc.qty):

				jmi_qr_code = frappe.new_doc('JMI QR Code')
				jmi_qr_code.barcode_constant = doc.barcode_constant

				if count == 0:
					roll_number = doc.from_roll_number
					start_sequence = doc.from_sequence_number
				elif r_num%2000 == 0:
					from_doc = frappe.get_doc("JMI QR Code",{'sequence_number':start_sequence})
					to_doc = frappe.get_doc("JMI QR Code",{'sequence_number':sequence_number})
					qr_doc = frappe.new_doc("Roll wise QR")
					qr_doc.roll_number = roll_number
					qr_doc.available_from_qr_code = from_doc.name
					qr_doc.available_end_qr_code = to_doc.name
					qr_doc.save(ignore_permissions=True)
					frappe.db.commit()
		
					start_sequence = prepare_sequence_number(sequence_number)
					roll_number = prepare_roll_number(roll_number)

				r_num += 1

				if count == 0:
					sequence_number = doc.from_sequence_number
				else:
					sequence_number = prepare_sequence_number(sequence_number)

				jmi_qr_code.roll_number = roll_number
				jmi_qr_code.sequence_number = sequence_number
				jmi_qr_code.save(ignore_permissions=True)
				frappe.db.commit()
			
			if not frappe.db.exists("Roll wise QR",{'roll_number':roll_number}):
				from_doc = frappe.get_doc("JMI QR Code",{'sequence_number':start_sequence})
				to_doc = frappe.get_doc("JMI QR Code",{'sequence_number':sequence_number})
				qr_doc = frappe.new_doc("Roll wise QR")
				qr_doc.roll_number = roll_number
				qr_doc.available_from_qr_code = from_doc.name
				qr_doc.available_end_qr_code = to_doc.name
				qty = int(sequence_number) - int(start_sequence)
				if qty+1 == 2000:
					qr_doc.status = "Full Available"
				else:
					qr_doc.status = "Partial Available"
				qr_doc.save(ignore_permissions=True)
				frappe.db.commit()


			frappe.db.set_value('JMI QR Code Builder', doc.name, 'status', 'Completed')
			doc.reload()
			frappe.db.set_value('QR Code Settings', None, 'qr_code_sequence_id', prepare_sequence_number(sequence_number))
			frappe.db.set_value('QR Code Settings', None, 'roll_number', prepare_roll_number(roll_number))
			frappe.db.commit()
	except Exception as exception:
		frappe.log_error(frappe.get_traceback())
		comment = frappe.get_doc({
			'doctype':'Comment',
			'comment_type':'Comment',
			'reference_doctype':doc.doctype,
			'reference_name':doc.name,
			'content': exception
		})
		comment.insert(ignore_permissions=True)
		frappe.db.commit()

def prepare_sequence_number(sequence_number):
	sequence_id = int(sequence_number) + 1
	length = len(str(sequence_id))
	if length<9:
		zero_count = 9-length
	new_sequence_number = '0' * zero_count
	new_sequence_number += str(sequence_id)
	return new_sequence_number


def prepare_roll_number(roll_number):
	roll_id = int(roll_number) + 1
	length = len(str(roll_id))
	if length<6:
		zero_count = 6-length
	new_roll_number = '0' * zero_count
	new_roll_number += str(roll_id)
	return new_roll_number
