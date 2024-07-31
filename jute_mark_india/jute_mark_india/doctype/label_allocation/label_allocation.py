# Copyright (c) 2023, admin and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
import json
from frappe.utils import flt

class LabelAllocation(Document):

	def autoname(self):
		if self.regional_office:
			series = 'JMI-QR-'+self.regional_office+'-'
			self.name = make_autoname(series)

	def validate(self):
		self.validate_roll_list()
		self.calculate_total_labels()


	def validate_roll_list(self):
		if self.is_ro_transfer:
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				if to_roll_number < from_roll_number:
					frappe.throw("To Roll is smaller than From Roll, Please select Proper To Roll Document!")
				else:
					roll_list = prepare_roll_list(from_roll_number,to_roll_number,user=self.from_ro_user)
					required_roll = int(int(self.requested_quantity)/2000)
					if len(roll_list) != required_roll:
						frappe.throw(_("You have selected more number of rolls. You need only:{} complete rolls").format(required_roll))
		else:
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				if to_roll_number < from_roll_number:
					frappe.throw("To Roll is smaller than From Roll, Please select Proper To Roll Document!")
				else:
					roll_list = prepare_roll_list(from_roll_number,to_roll_number,is_ro=self.is_ro)
					required_roll = int(int(self.requested_quantity)/2000)
					if len(roll_list) != required_roll:
						frappe.throw(_("You have selected more number of rolls. You need only:{} complete rolls").format(required_roll))


	def calculate_total_labels(self):
		label_count = 0
		if self.is_ro_transfer:
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				roll_list = prepare_roll_list(from_roll_number,to_roll_number,user=self.from_ro_user)
				label_count += (len(roll_list)*2000)
			if self.partial_roll_selection:
				labels = get_label_count(self.from_qr_code, self.to_qr_code)
				label_count += labels
			elif self.complete_roll_selection:
				rem_qty = int(self.requested_quantity)%2000
				roll_doc =  frappe.get_doc("Roll wise QR",self.complete_roll_selection)
				self.from_qr_code = roll_doc.available_from_qr_code
				from_seq_id = frappe.db.get_value("JMI QR Code",roll_doc.available_from_qr_code,['sequence_number'])
				to_seq_id = prepare_new_seq_id(int(from_seq_id)+rem_qty-1)
				to_qr_doc = frappe.get_doc("JMI QR Code",{'sequence_number':to_seq_id})
				self.to_qr_code = to_qr_doc.name
				label_count += get_label_count(self.from_qr_code, self.to_qr_code)
		else:
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				roll_list = prepare_roll_list(from_roll_number,to_roll_number,is_ro=self.is_ro)
				label_count += (len(roll_list)*2000)
			if self.partial_roll_selection:
				labels = get_label_count(self.from_qr_code, self.to_qr_code)
				label_count += labels
			elif self.complete_roll_selection:
				rem_qty = int(self.requested_quantity)%2000
				roll_doc =  frappe.get_doc("Roll wise QR",self.complete_roll_selection)
				self.from_qr_code = roll_doc.available_from_qr_code
				from_seq_id = frappe.db.get_value("JMI QR Code",roll_doc.available_from_qr_code,['sequence_number'])
				to_seq_id = prepare_new_seq_id(int(from_seq_id)+rem_qty-1)
				to_qr_doc = frappe.get_doc("JMI QR Code",{'sequence_number':to_seq_id})
				self.to_qr_code = to_qr_doc.name
				label_count += get_label_count(self.from_qr_code, self.to_qr_code)
		self.total_no_of_labels = label_count

	# def before_submit(self):
	# 	user_role = frappe.get_roles(frappe.session.user)
	# 	if not self.is_paid and "JMI User" in user_role:
	# 		frappe.throw("Please Proceed Payment First !")
			
	def on_submit(self):
		if self.is_ro_transfer:
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				roll_list = prepare_roll_list(from_roll_number,to_roll_number,user=self.from_ro_user)
				for roll_doc in roll_list:
					labels = get_labels_within_range(roll_doc.available_from_qr_code,roll_doc.available_end_qr_code,"Allocated to RO")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
						allocate_rolls(roll_doc,self.requested_by, self.regional_office,"Allocated to RO Full")
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
			if self.partial_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.partial_roll_selection)
				labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
				if labels:
					frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
					allocate_rolls(roll_doc,self.requested_by, self.regional_office,"Allocated to RO Partial",self.from_qr_code,self.to_qr_code)
				else:
					frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
			elif self.complete_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.complete_roll_selection)
				labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
				if labels:
					frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
					allocate_rolls(roll_doc,self.requested_by, self.regional_office,"Allocated to RO Partial",self.from_qr_code,self.to_qr_code)
				else:
					frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
		else:
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				roll_list = prepare_roll_list(from_roll_number,to_roll_number,is_ro=self.is_ro)
				for roll_doc in roll_list:
					if self.is_ro:
						labels = get_labels_within_range(roll_doc.available_from_qr_code,roll_doc.available_end_qr_code)
						if labels:
							frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
							allocate_rolls(roll_doc,self.requested_by, self.regional_office,"Allocated to RO Full")
						else:
							frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
					else:
						labels = get_labels_within_range(roll_doc.available_from_qr_code,roll_doc.available_end_qr_code,"Allocated to RO")
						if labels:
							frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels, status= "Allocated", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
							allocate_rolls(roll_doc,self.requested_by, self.regional_office, "Allocated")
						else:
							frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
			if self.partial_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.partial_roll_selection)
				if self.is_ro:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code)
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
						allocate_rolls(roll_doc,self.requested_by, self.regional_office,"Allocated to RO Partial",self.from_qr_code,self.to_qr_code)
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
				else:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels, status= "Allocated", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
						allocate_rolls(roll_doc,self.requested_by, self.regional_office, "Allocated",self.from_qr_code,self.to_qr_code)
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))

			elif self.complete_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.complete_roll_selection)
				if self.is_ro:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code)
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number, allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
						allocate_rolls(roll_doc,self.requested_by, self.regional_office,"Allocated to RO Partial",self.from_qr_code,self.to_qr_code)
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
				else:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels, status= "Allocated", app__reg_number=self.app__reg_number,allocate=1,requsted_user_name=self.requested_by, regional_office=self.regional_office, queue="long")
						allocate_rolls(roll_doc,self.requested_by, self.regional_office, "Allocated",self.from_qr_code,self.to_qr_code)
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
		self.calculate_allcated_percent()


	def on_cancel(self):
		if self.is_ro_transfer:
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				roll_list = prepare_roll_list(from_roll_number,to_roll_number,user=self.requested_by)
				for roll_doc in roll_list:
					labels = get_labels_within_range(roll_doc.available_from_qr_code,roll_doc.available_end_qr_code,"Allocated to RO")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=0,requsted_user_name=self.from_ro_user, regional_office=self.from_ro_regional_office, queue="long")
						deallocate_rolls(roll_doc,"Allocated to RO Full",self.from_ro_user,self.from_ro_regional_office)
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
			if self.partial_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.partial_roll_selection)
				labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
				if labels:
					frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=0,requsted_user_name=self.from_ro_user, regional_office=self.from_ro_regional_office, queue="long")
					deallocate_rolls(roll_doc,"Partial Available",self.from_ro_user,self.from_ro_regional_office)
				else:
					frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
			elif self.complete_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.complete_roll_selection)
				labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
				if labels:
					frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=0,requsted_user_name=self.from_ro_user, regional_office=self.from_ro_regional_office, queue="long")
					deallocate_rolls(roll_doc,"Partial Available",self.from_ro_user,self.from_ro_regional_office)
				else:
					frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
		else:
			user = frappe.session.user
			regional_office = frappe.db.get_value("User wise RO",user,'regional_office')
			if self.from_roll:
				from_roll_number = frappe.db.get_value("Roll wise QR",self.from_roll,'roll_number')
				to_roll_number = frappe.db.get_value("Roll wise QR",self.to_roll,'roll_number')
				roll_list = prepare_roll_list(from_roll_number,to_roll_number,is_ro=self.is_ro,allocate=1)
				for roll_doc in roll_list:
					if self.is_ro:
						labels = get_labels_within_range(roll_doc.available_from_qr_code,roll_doc.available_end_qr_code,"Allocated to RO")
						if labels:
							frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Available", app__reg_number=self.app__reg_number,allocate=0, queue="long")
							deallocate_rolls(roll_doc,"Full Available")
						else:
							frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
					else:
						labels = get_labels_within_range(roll_doc.available_from_qr_code,roll_doc.available_end_qr_code,"Allocated")
						if labels:
							frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels, status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=0,requsted_user_name=user, regional_office=regional_office, queue="long")
							deallocate_rolls(roll_doc, "Allocated to RO Full", requsted_user_name=user,regional_office=regional_office)
						else:
							frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
			if self.partial_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.partial_roll_selection)
				if self.is_ro:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Available", app__reg_number=self.app__reg_number,allocate=0, queue="long")
						deallocate_rolls(roll_doc,"Partial Available")
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
				else:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels, status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=0,requsted_user_name=user, regional_office=regional_office, queue="long")
						deallocate_rolls(roll_doc, "Allocated to RO Partial", requsted_user_name=user,regional_office=regional_office)
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))

			elif self.complete_roll_selection:
				roll_doc = frappe.get_doc("Roll wise QR",self.complete_roll_selection)
				if self.is_ro:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated to RO")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels,status= "Available", app__reg_number=self.app__reg_number,allocate=0, queue="long")
						deallocate_rolls(roll_doc,"Partial Available")
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
				else:
					labels = get_labels_within_range(self.from_qr_code,self.to_qr_code,"Allocated")
					if labels:
						frappe.enqueue(allocate_or_reallocate_multiple_labels, jmi_qr_codes=labels, status= "Allocated to RO", app__reg_number=self.app__reg_number,allocate=0,requsted_user_name=user, regional_office=regional_office, queue="long")
						deallocate_rolls(roll_doc, "Allocated to RO Partial",requsted_user_name=user,regional_office=regional_office)
					else:
						frappe.throw(_('No labels found in this Roll:{}  Please Check!'.format(roll_doc.name)))
		self.calculate_allcated_percent(on_cancel=True)

	def calculate_allcated_percent(self, on_cancel=False):
		if self.requested_quantity and self.request_for_label:
			required_qty = frappe.db.get_value("Request for Label", self.request_for_label, "required_qty")
			if required_qty:
				allocated_qty = frappe.db.sql(f"""
					select sum(requested_quantity) from `tabLabel Allocation`
					where request_for_label = '{self.request_for_label}' and
					name <> '{self.name}' and docstatus = 1
				""")[0][0] or 0
				curr_qty = self.requested_quantity
				if not on_cancel:
					allocated_qty = flt(allocated_qty) + flt(curr_qty)
				allocated_percentage = flt(allocated_qty / required_qty * 100)
				if allocated_percentage:
					frappe.db.sql(f"""
						update `tabRequest for Label` set allocated_percentage = {allocated_percentage}
						where name = '{self.request_for_label}'
					""")
					frappe.db.commit()

@frappe.whitelist()
def get_labels_within_range(from_qr_code, to_qr_code, status='Available'):
	if not frappe.db.exists('JMI QR Code', from_qr_code):
		frappe.throw('From JMI QR Code does not exists. Please check once again')
	if not frappe.db.exists('JMI QR Code', to_qr_code):
		frappe.throw('To JMI QR Code does not exists. Please check once again')
	query = """
		SELECT
			name
		FROM
			`tabJMI QR Code` as jmiqr
		WHERE
			jmiqr.status = %(status)s AND
			jmiqr.name >= %(from_qr_code)s AND
			jmiqr.name <= %(to_qr_code)s
	"""
	doc_list = frappe.db.sql(query.format(),{ 'from_qr_code':from_qr_code, 'to_qr_code':to_qr_code, 'status':status }, as_dict = 1)
	return doc_list


@frappe.whitelist()
def allocate_or_reallocate_multiple_labels(jmi_qr_codes, status, app__reg_number=None, allocate=1,requsted_user_name=None,regional_office=None):
	'''
		Method to allocate or reallocate JMI QR Codes
		args:
			jmi_qr_codes: List of JMI QR Codes
			allocate: 1 for allocate and 0 for reallocate
			regional_office: Regional Office
	'''
	try:
		for jmi_qr_code in jmi_qr_codes:
			if allocate:
				allocate_jmi_qr_code(jmi_qr_code, status,regional_office,requsted_user_name,app__reg_number)
			else:
				reallocate_jmi_qr_code(jmi_qr_code,status,app__reg_number, regional_office=regional_office,requsted_user_name=requsted_user_name)
	except  Exception as exception:
		frappe.log_error(frappe.get_traceback())

@frappe.whitelist()
def allocate_jmi_qr_code(jmi_qr_code,status, regional_office,requsted_user_name,app__reg_number):
	'''
		Method to allocate JMI QR Codes to regional_office
		args:
			jmi_qr_codes: JMI QR Code
			regional_office: Regional Office
	'''
	frappe.db.set_value('JMI QR Code',jmi_qr_code, 'allocated_to_user',requsted_user_name)
	frappe.db.set_value('JMI QR Code', jmi_qr_code, 'allocated_to', regional_office)
	frappe.db.set_value('JMI QR Code', jmi_qr_code, 'status', status)
	frappe.db.set_value('JMI QR Code', jmi_qr_code, 'register_no', app__reg_number)
	frappe.db.commit()

@frappe.whitelist()
def reallocate_jmi_qr_code(jmi_qr_code,status,app__reg_number,regional_office=None,requsted_user_name=None):
	'''
		Method to reallocate JMI QR Codes
		args:
			jmi_qr_code: JMI QR Code
	'''

	if regional_office and requsted_user_name:
		frappe.db.set_value('JMI QR Code', jmi_qr_code, 'allocated_to', regional_office)
		frappe.db.set_value('JMI QR Code',jmi_qr_code, 'allocated_to_user',requsted_user_name)
		frappe.db.set_value('JMI QR Code', jmi_qr_code, 'status', status)
		frappe.db.set_value('JMI QR Code', jmi_qr_code, 'register_no', app__reg_number)
		frappe.db.commit()
	else:
		frappe.db.set_value('JMI QR Code', jmi_qr_code, 'allocated_to', '')
		frappe.db.set_value('JMI QR Code',jmi_qr_code, 'allocated_to_user','')
		frappe.db.set_value('JMI QR Code', jmi_qr_code, 'status', status)
		frappe.db.set_value('JMI QR Code', jmi_qr_code, 'register_no', app__reg_number)
		frappe.db.commit()



#setting from_qr_code and to_qr_code field for partial selection field
@frappe.whitelist()
def set_for_partial(roll,qty):
	roll_doc = frappe.get_doc("Roll wise QR",roll)
	from_doc = roll_doc.available_from_qr_code
	if roll_doc.available_qantity == int(qty):
		to_doc = roll_doc.available_end_qr_code
		return(from_doc,to_doc)
	else:
		from_seq_id = frappe.db.get_value("JMI QR Code",from_doc,['sequence_number'])
		end_id = str(int(from_seq_id) + int(qty) - 1)
		end_id = end_id.zfill(9)
		to_doc = frappe.get_doc("JMI QR Code",{'sequence_number':end_id})
		return (from_doc,to_doc.name)


@frappe.whitelist()
def set_to_roll(from_roll,no_of_rolls):
	from_roll_number = frappe.db.get_value("Roll wise QR",from_roll,'roll_number')
	to_roll_number = prepare_roll_number(int(from_roll_number) + int(no_of_rolls) -1)
	user = frappe.session.user
	if user == "Administrator":
		if frappe.db.exists("Roll wise QR",{'roll_number':to_roll_number,'available_qantity':2000,'status':"Full Available"}):
			doc_name = frappe.get_doc("Roll wise QR",{'roll_number':to_roll_number,'available_qantity':2000,'status':"Full Available"}).name
		else:
			frappe.throw(_("Their is No Roll available in continuous sequence of Roll:{0} for Qty of Roll:{1}".format(from_roll,int(no_of_rolls))))
	else:
		if frappe.db.exists("Roll wise QR",{'roll_number':to_roll_number,'available_qantity':2000,'status':"Allocated to RO Full",'allocated_to_user':user}):
			doc_name = frappe.get_doc("Roll wise QR",{'roll_number':to_roll_number,'available_qantity':2000,'status':"Allocated to RO Full",'allocated_to_user':user}).name
		else:
			frappe.throw(_("Their is No Roll available in continuous sequence of Roll:{0} for Qty of Roll:{1}".format(from_roll,int(no_of_rolls))))

	return doc_name


def deallocate_rolls(roll_doc,status,requsted_user_name=None,regional_office=None):
	roll_doc.status = status

	if requsted_user_name and regional_office:
		roll_doc.allocated_to_user = requsted_user_name
		roll_doc.allocated_to = regional_office
	else:
		roll_doc.allocated_to_user = ''
		roll_doc.allocated_to = ''

	roll_doc.save(ignore_permissions=True)
	frappe.db.commit()



# updating fields from Roll Wise QR master regarding allocation
def allocate_rolls(roll_doc,requsted_user_name, regional_office,status,start=None, end=None):
	if start and end:
		if roll_doc.available_from_qr_code==start and roll_doc.available_end_qr_code==end:
			roll_doc.status = status
		else:
			new_roll_doc = frappe.new_doc("Roll wise QR")
			new_roll_doc.roll_number = roll_doc.roll_number+"_part"
			end_seq_id = frappe.db.get_value("JMI QR Code",end,['sequence_number'])
			from_id = int(end_seq_id) + 1
			from_id = prepare_new_seq_id(from_id)
			from_doc = frappe.get_doc("JMI QR Code",{'sequence_number':from_id})
			new_roll_doc.available_from_qr_code = from_doc.name
			new_roll_doc.available_end_qr_code = roll_doc.available_end_qr_code
			if status == "Allocated to RO Partial":
				new_roll_doc.status = "Partial Available"
			else:
				new_roll_doc.status = "Allocated to RO Partial"
				user = frappe.session.user
				new_roll_doc.allocated_to_user = user
				new_roll_doc.allocated_to = frappe.db.get_value("User wise RO",user,'regional_office')
			new_roll_doc.save(ignore_permissions=True)
			frappe.db.commit()
			roll_doc.available_end_qr_code = end
			roll_doc.status = status
	else:
		roll_doc.status = status
	if roll_doc.status == "Allocated":
		roll_doc.available_qantity = 0
	roll_doc.allocated_to = regional_office
	roll_doc.allocated_to_user = requsted_user_name
	roll_doc.save(ignore_permissions=True)
	frappe.db.commit()


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def set_filter_complete_roll_selection(doctype, txt, searchfield, start, page_len, filters):
	user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if user != "Administrator":
		return frappe.db.sql(""" select name  from `tabRoll wise QR` where status="Allocated to RO Full" and allocated_to_user='{}' """.format(user))
	else:
		return frappe.db.sql(""" select name  from `tabRoll wise QR` where status="Full Available" """)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def set_filter_partial_selection(doctype, txt, searchfield, start, page_len, filters):
	user = frappe.session.user
	user_roles = frappe.get_roles(user)
	if user != "Administrator":
		if filters.get("qty")!=0:
			return frappe.db.sql(""" select name  from `tabRoll wise QR` where status="Allocated to RO Partial" and available_qantity>='{0}' and allocated_to_user='{1}' """.format(filters.get("qty"),user))
		else:
			return frappe.db.sql(""" select name  from `tabRoll wise QR` where status="Allocated to RO Partial" and available_qantity>=2000 and allocated_to_user='{}' """.format(user))
	else:
		if filters.get("qty")!=0:
			return frappe.db.sql(""" select name from `tabRoll wise QR` where status = "Partial Available" and available_qantity>='{}' """.format(filters.get("qty")))
		else:
			return frappe.db.sql(""" select name from `tabRoll wise QR` where status = "Partial Available" and available_qantity>2000""")



def prepare_roll_number(num):
	num = str(num)
	next_id = num.zfill(6)
	return next_id

def prepare_new_seq_id(num):
	num = str(num)
	seq_id = num.zfill(9)
	return seq_id


def prepare_roll_list(from_roll_number,to_roll_number,is_ro=0,allocate=0,user=None):
	if user:
		roll_list = []
		roll_nums = int(to_roll_number) - int(from_roll_number)
		num = int(from_roll_number)
		while num <= int(to_roll_number):
			next_roll_number = prepare_roll_number(num)
			if frappe.db.exists("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated to RO Full','allocated_to_user':user}):
				doc = frappe.get_doc("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated to RO Full','allocated_to_user':user})
			else:
				frappe.throw("Roll Number is NOT Available in this From Roll and To Roll Selection")

			roll_list.append(doc)

			num+=1
	else:
		login_user = frappe.session.user
		roll_list = []
		roll_nums = int(to_roll_number) - int(from_roll_number)
		num = int(from_roll_number)
		if is_ro:
			while num <= int(to_roll_number):
				next_roll_number = prepare_roll_number(num)
				if allocate==0:
					if frappe.db.exists("Roll wise QR",{'roll_number':next_roll_number,'status':'Full Available'}):
						doc = frappe.get_doc("Roll wise QR",{'roll_number':next_roll_number,'status':'Full Available'})
					else:
						frappe.throw("Roll Number is NOT Available in this From Roll and To Roll Selection")
				else:
					if frappe.db.exists("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated to RO Full'}):
						doc = frappe.get_doc("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated to RO Full'})
					else:
						frappe.throw("Roll Number is NOT Available in this From Roll and To Roll Selection")
				roll_list.append(doc)

				num+=1
		else:
			while num <= int(to_roll_number):
				next_roll_number = prepare_roll_number(num)
				if allocate == 0:
					if frappe.db.exists("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated to RO Full','allocated_to_user':login_user}):
						doc = frappe.get_doc("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated to RO Full','allocated_to_user':login_user})
					else:
						frappe.throw("Roll Number is NOT Available in this From Roll and To Roll Selection")
				else:
					if frappe.db.exists("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated'}):
						doc = frappe.get_doc("Roll wise QR",{'roll_number':next_roll_number,'status':'Allocated'})
					else:
						frappe.throw("Roll Number is NOT Available in this From Roll and To Roll Selection")
				roll_list.append(doc)

				num+=1
	return roll_list

def get_label_count(from_qr_code, to_qr_code):
	from_seq_id = frappe.db.get_value("JMI QR Code",from_qr_code,'sequence_number')
	end_seq_id = frappe.db.get_value("JMI QR Code", to_qr_code,'sequence_number')
	if from_seq_id and end_seq_id:
		diff = int(end_seq_id) - int(from_seq_id)
		return (diff+1)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def set_filter_from_ro_user(doctype, txt, searchfield, start, page_len, filters):
	return frappe.db.sql(""" select u.name from `tabUser` u join `tabHas Role` hr on u.name=hr.parent where hr.parenttype="User" and   hr.role = "Regional Officer(RO)"; """)


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def complete_roll_ro_transfer(doctype, txt, searchfield, start, page_len, filters):
	if frappe.session.user == "Administrator":
		return frappe.db.sql(""" select name  from `tabRoll wise QR` where status="Allocated to RO Full" and allocated_to_user='{}' """.format(filters.get('user')))
	else:
		frappe.throw("RO to RO Transfer not allowed for user other than Admin!!!")


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def set_filter_partial_ro_transfer(doctype, txt, searchfield, start, page_len, filters):
	user = filters.get('user')
	user_roles = frappe.get_roles(user)
	if user != "Administrator":
		if filters.get("qty")!=0:
			return frappe.db.sql(""" select name  from `tabRoll wise QR` where status="Allocated to RO Partial" and available_qantity>='{0}' and allocated_to_user='{1}' """.format(filters.get("qty"),user))
		else:
			return frappe.db.sql(""" select name  from `tabRoll wise QR` where status="Allocated to RO Partial" and available_qantity>=2000 and allocated_to_user='{}' """.format(user))
	else:
		frappe.throw("You have selected a Administrator user!!! Please select another RO User!!")

#setting to roll  in RO to RO Transfer
@frappe.whitelist()
def set_to_roll_ro_transfer(from_roll,no_of_rolls,user):
	from_roll_number = frappe.db.get_value("Roll wise QR",from_roll,'roll_number')
	to_roll_number = prepare_roll_number(int(from_roll_number) + int(no_of_rolls) -1)
	if frappe.session.user == "Administrator":
		if frappe.db.exists("Roll wise QR",{'roll_number':to_roll_number,'available_qantity':2000,'status':"Allocated to RO Full",'allocated_to_user':user}):
			doc_name = frappe.get_doc("Roll wise QR",{'roll_number':to_roll_number,'available_qantity':2000,'status':"Allocated to RO Full",'allocated_to_user':user}).name
		else:
			frappe.throw(_("Their is No Roll available in continuous sequence of Roll:{0} for Qty of Roll:{1}".format(from_roll,int(no_of_rolls))))
	return doc_name