# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Pincode(Document):
	def validate(self):
		self.validate_pincode()

	def validate_pincode(self):
		if self.pincode:
			if len(str(self.pincode))!=6 or not self.pincode.isnumeric():
				frappe.throw(frappe._("Pincode should be 6 digit number!"))
