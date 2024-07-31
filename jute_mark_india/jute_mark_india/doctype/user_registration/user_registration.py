# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class UserRegistration(Document):
	def after_insert(self):
		self.send_email_otp()

	def send_email_otp(self):
		if self.email_id and self.otp:
			subject = 'OTP for JMI Registration'
			body = '''Dear user,<br>
			OTP for JMI Registration is : {0}
			'''.format(self.otp)
			frappe.sendmail(recipients=[self.email_id],subject=subject, message=body, delayed=False)
