import frappe
import re
from frappe.utils import today,getdate, has_common

@frappe.whitelist()
def create_todo(allocated_to, description, reference_type, reference_name, assigned_by=frappe.session.user):
	todo_doc = frappe.new_doc('ToDo')
	todo_doc.allocated_to = allocated_to
	todo_doc.description = description
	todo_doc.reference_type = reference_type
	todo_doc.reference_name = reference_name
	todo_doc.assigned_by = assigned_by
	todo_doc.flags.ignore_mandatory = True
	todo_doc.save(ignore_permissions=True)
	frappe.db.commit()

@frappe.whitelist()
def get_site_details(registration_no, assigned_to):
    '''
        Method to get site details assigned to selected VO
    '''
    query = '''
        SELECT
            tdp.name_of_unit__outlet as site_name,
            tdp.address as site_address
        FROM
            `tabJute Mark India Registration form` as jmi,
            `tabTextile_Details of Production Units or Retailer Sales Outlets` as tdp
        WHERE
            jmi.name = tdp.parent AND
            tdp.assign_to = %(assigned_to)s
    '''
    output = frappe.db.sql(query.format(), { 'assigned_to':assigned_to }, as_dict = 1)
    return output

@frappe.whitelist()
def schedule_site_visit(application_no, site_name, assigned_for=None, address_visited=None, no_of_male_artisan=0, no_of_female_artisan=0, no_of_other_artisan=0, is_primary_site=0):
	if not assigned_for:
		assigned_for = frappe.session.user
	schedule_doc = frappe.new_doc('Actual Site Visit Plan')
	schedule_doc.application_no = application_no
	schedule_doc.address_line1 = site_name
	schedule_doc.assigned_for = assigned_for
	if address_visited:
		schedule_doc.address_visited = address_visited
	schedule_doc.no_of_male_artisan = no_of_male_artisan
	schedule_doc.no_of_female_artisan = no_of_female_artisan
	schedule_doc.no_of_other_artisan = no_of_other_artisan
	schedule_doc.is_primary_site = is_primary_site
	schedule_doc.flags.ignore_mandatory = True
	schedule_doc.save(ignore_permissions=True)
	frappe.db.commit()
	return schedule_doc.name

@frappe.whitelist()
def validate_njb_number(njb_number):
	''' Method to Validate NJB Number '''
	regex = "^[A-Z]{3}[0-9]{2}[A-Z]{3}[0-9]{9}$"
	p = re.compile(regex)
	if (njb_number == None):
		return False
	if(re.search(p, njb_number)):
		return True
	else:
		return False

@frappe.whitelist()
def validate_udayam_adhar(udyog_aadhar):
	'''Method to validate UDAYAM Aadhar'''
	regex = "^[A-Z]{6}-[A-Z]{2}-[0-9]{2}-[0-9]{7}$"
	p = re.compile(regex)
	if(udyog_aadhar == None):
		return False
	if(re.search(p, udyog_aadhar)):
		return True
	else:
		return False

# @frappe.whitelist()
# def check_udyog_aadhar(doc):
#     # Check if the Udyog Aadhar already exists in the 'Jute Mark India Registration form' doctype
#     existing_udyog_aadhar = frappe.get_all("Jute Mark India Registration form", filters={"udyog_aadhar": doc.udyog_aadhar}, fields="name")
#
#     if existing_udyog_aadhar:
#         # Udyog Aadhar number already exists
#         frappe.throw('Udyog Aadhar already exists')  # This line will raise an error if the Udyog Aadhar already exists
#     else:
#         # Udyog Aadhar number is unique
#         return False

@frappe.whitelist()
def is_able_to_create_appeal(application_no):
	'''
		Method to check wether Appel can be created against this application
	'''
	able_to_create_appeal = 0
	if frappe.db.exists('Jute Mark India Registration form', application_no):
		workflow_state = frappe.db.get_value('Jute Mark India Registration form', application_no, 'workflow_state')
		last_update_on = frappe.db.get_value('Jute Mark India Registration form', application_no, 'modified')
		current_date = getdate(today())
		if workflow_state in ['Approved By HO', 'Rejected by HO', 'Approved By RO', 'Rejected by RO']:
			if current_date <= getdate(frappe.utils.add_to_date(last_update_on, days=15)):
				if not frappe.db.exists('JMI Appeal', { 'application_no':application_no, 'appeal_type': [ 'in', ['Appeal for Rejection', 'Appeal for Approval']] }):
					able_to_create_appeal = 1
	return able_to_create_appeal

@frappe.whitelist()
def is_able_to_create_escalation(application_no):
	'''
		Method to check wether Escalation can be created against this application
	'''
	able_to_create_escalation = 0
	if frappe.db.exists('Jute Mark India Registration form', application_no):
		if frappe.db.exists('JMI Appeal', { 'application_no':application_no, 'appeal_type': [ 'in', ['Appeal for Rejection', 'Appeal for Approval']] }):
			previous_appealing_date = frappe.db.get_value('JMI Appeal', { 'application_no':application_no, 'appeal_type': [ 'in', ['Appeal for Rejection', 'Appeal for Approval']] }, 'appealing_date')
			current_date = getdate(today())
			if current_date > getdate(frappe.utils.add_to_date(previous_appealing_date, days=10)):
				if not frappe.db.exists('JMI Appeal', { 'application_no':application_no, 'appeal_type':'Appeal for Escalation' }):
					able_to_create_escalation = 1
	return able_to_create_escalation

@frappe.whitelist()
def is_site_details_filled(application_no):
	'''
		Method to check wether Site Details filled or not
	'''
	site_details_filled = 0
	if frappe.db.exists('Jute Mark India Registration form', application_no):
		jmi_doc = frappe.get_doc('Jute Mark India Registration form', application_no)
		if jmi_doc.textile_details_of_production_units_or_retailer_sales_outlets:
			site_details_filled = 1
	return site_details_filled

@frappe.whitelist()
def is_sampling_required(application_no):
	'''
		Method to check wether Sampling is required or not
	'''
	sampling_required = 0
	if frappe.db.exists('Jute Mark India Registration form', application_no):
		jmi_doc = frappe.get_doc('Jute Mark India Registration form', application_no)
		if jmi_doc.textile_details_of_product:
			for textile_details in jmi_doc.textile_details_of_product:
				if textile_details.test_report_details == 'Not Available':
					sampling_required = 1
	return sampling_required

@frappe.whitelist()
def get_regional_office(state, district):
	'''
		Method to get Regional Office with State and Distirct
	'''
	regional_office = False
	query = """
		select
			distinct ro.name
		from
			`tabRegional Office` as ro,
			`tabStates` as s,
			`tabDistricts` as d
		where
			ro.name = s.parent AND
			ro.name = d.parent AND
			s.state = %(state)s AND
			d.district = %(district)s
	"""
	regional_offices = frappe.db.sql(query.format(),{ 'state' : state, 'district' : district }, as_dict = 1)
	if regional_offices:
		regional_office = regional_offices[0].get('name')
	return regional_office

@frappe.whitelist()
def user_registration_hourly_scheduler():
	'''
		Method to Clear User Registration logs via scheduler
	'''
	if frappe.db.exists('User Registration', { 'verified':1 }):
		user_registrations = frappe.get_all('User Registration', { 'verified':1 })
		if user_registrations:
			for user_registration in user_registrations:
				frappe.db.delete('User Registration', user_registration.name)
				frappe.db.commit()
	time_limit = frappe.utils.get_datetime(frappe.utils.add_days(frappe.utils.now(), -0.3))
	if frappe.db.exists('User Registration', { 'verified':0, 'creation':[ '<', time_limit] }):
		user_registrations = frappe.get_all('User Registration', { 'verified':0, 'creation':[ '<', time_limit] })
		if user_registrations:
			for user_registration in user_registrations:
				frappe.db.delete('User Registration', user_registration.name)
				frappe.db.commit()

@frappe.whitelist()
def get_primary_site_details(application_no):
	''' Method to get Primary site details '''
	site_details = False
	if frappe.db.exists('Jute Mark India Registration form', application_no):
		if frappe.db.exists('Actual Site Visit Plan', { 'application_no':application_no, 'is_primary_site':1 }):
			site_details = frappe.get_doc('Actual Site Visit Plan', { 'application_no':application_no, 'is_primary_site':1 })
	return site_details

@frappe.whitelist()
def get_page_route():
	user = frappe.session.user
	route = '/app/'
	user_roles = frappe.get_roles(user)
	dashboard_roles = ["Administrator", "Regional Officer(RO)", "HO", "Verification Officer(VO)"]
	if user == 'Administrator' or has_common(dashboard_roles, user_roles):
		route = "/app/dashboard-view/JMI%20Dashboard"
	elif has_common(["JMI User"], user_roles):
		route = "/app/jmi-user"
	return route
