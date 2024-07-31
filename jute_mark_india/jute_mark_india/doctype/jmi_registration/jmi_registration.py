# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.print_format import download_pdf
from jute_mark_india.jute_mark_india.pdf_utils import *
from jute_mark_india.api.mobile_api import get_on_site_verification_form
from frappe.model.document import Document
import urllib.request 

class JMIRegistration(Document):
	def validate(self):
		if self.application_number:
			if frappe.db.exists('Actual Site Visit Plan', { 'application_no': self.application_number, 'is_primary_site': 1 }):
				site_visit_id = frappe.db.get_value('Actual Site Visit Plan', { 'application_no': self.application_number, 'is_primary_site': 1 })
				self.on_site_verification_date = frappe.db.get_value('Actual Site Visit Plan', site_visit_id, 'visit_planed_on')
				on_site_verification_form = get_on_site_verification_form(self.application_number)
				if on_site_verification_form:
					on_site_doc = frappe.get_doc('On-Site Verification Form', on_site_verification_form)
					if on_site_doc.no_of_labels:
						self.no_of_labels = on_site_doc.no_of_labels

	

	def on_submit(self):
		pdf_link = create_pdf_attachment(self.doctype, self.name, 'JMI Registration Letter')
		if pdf_link:
			self.registration_letter = pdf_link

@frappe.whitelist()
def create_pdf_attachment(doctype, docname, print_format):
    doctype_folder = create_folder(_(doctype), "Home")
    title_folder = create_folder(docname, doctype_folder)
    pdf_data = get_pdf_data(doctype, docname, print_format)
    file_ref = save_and_attach(pdf_data, doctype, docname, title_folder)
    pdf_link = file_ref.file_url
    return pdf_link
