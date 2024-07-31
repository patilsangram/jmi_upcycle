# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
import datetime
# import calendar
import math
from frappe.model.document import Document

class RequestForLabelFulfilment(Document):
	def onload(self):
		self.label_balanced = self.label_allotted -self.label_used
		# current_date= datetime.date.today()
		# current_month = current_date.month
		current_month = self.application_date.month
		print ("----------current-month --",current_month)
		current_label = 12 - current_month
		label_allot = current_label*(self.label_allotted/12)
		self.monthly_allotted_labels = round(self.label_allotted/12)
		self.labels_allotted_from_current_month = current_label*(self.label_allotted/12)
		print("\n labels_allotted_from_current_month-",round(self.labels_allotted_from_current_month),"\n-current_label---",label_allot,"calculated=",current_label*(self.label_allotted/12))
		
		