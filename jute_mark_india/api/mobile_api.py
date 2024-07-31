import frappe
import json
import re
import os
from frappe.utils import getdate, today, add_to_date, flt
from jute_mark_india.www.registration import register, verify_otp
from jute_mark_india.jute_mark_india.utils import validate_njb_number, is_able_to_create_appeal, is_able_to_create_escalation, is_site_details_filled, is_sampling_required, get_primary_site_details, validate_udayam_adhar
from datetime import datetime, date


@frappe.whitelist(allow_guest=True)
def response(message, data, status_code):
    '''method to generates responses of an API
       args:
            message : response message string
            data : json object of the data
            status_code : status of the request'''
    frappe.clear_messages()
    frappe.local.response["message"] = message
    frappe.local.response["data"] = data
    frappe.local.response["http_status_code"] = status_code
    return

@frappe.whitelist(allow_guest=True)
def login(login_id, password, device_token=None):
    '''
        API for user login
        args:
            login_id : username/email of the user
            password : user password
    '''
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=login_id, pwd=password)
        login_manager.post_login()
        api_generate = generate_keys(frappe.session.user)
        user = frappe.get_doc("User", frappe.session.user)
        roles = frappe.get_roles(frappe.session.user)
        role = 'Guest'
        if roles:
            if 'All' in roles:
                roles.remove('All')
            if 'Guest' in roles:
                roles.remove('Guest')
            if len(roles)>0:
                role = roles[0]
        data = {
            "sid": frappe.session.sid,
            "api_key": user.api_key,
            "api_secret": api_generate,
            "is_active": user.enabled,
            "user_id": user.username,
            "full_name": user.full_name,
            "email_id": user.name,
            "mobile_number": user.mobile_no,
            "roles": role
            }
        if device_token:
            add_new_device(login_id, device_token)
        return response("Authentication Success", data, 200)
    except frappe.exceptions.AuthenticationError:
        return response("Invalid login credentials!", {}, 400)

def generate_keys(user):
    '''
        method generates api secret for a user
        args:
            user : username of the user
    '''
    if frappe.db.exists("User", user):
        user_details = frappe.get_doc("User", user)
        api_secret =  frappe.generate_hash(length=15)
        if not user_details.api_key:
            api_key = frappe.generate_hash(length=15)
            user_details.api_key = api_key
        user_details.api_secret = api_secret
        user_details.save()
        return api_secret

@frappe.whitelist(allow_guest=True)
def get_country(country_name=None):
    '''Method to get Country List '''
    try:
        if country_name:
            country_list = frappe.get_all('Country', fields = ['country_name', 'code as country_code'], filters={'country_name': ['like', '%' + country_name + '%' ]})
        else:
            country_list = frappe.get_all('Country', fields = ['country_name', 'code as country_code'])
        if len(country_list)>0:
            response('Data get sucessfully', country_list, 200)
        else:
            response('Data not found', [], 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_country", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_state(country_code, state_name=None):
    '''
        Method to get States in given country
        args:
            country_code : Country Code of Country
    '''
    try:
        if frappe.db.exists('Country', { 'code': country_code }):
            country_name = frappe.db.get_value('Country', { 'code': country_code })
            if state_name:
                state_list = frappe.get_all('State', filters={ 'country_name':country_name, 'state_name': ['like', '%' + state_name + '%' ]}, fields=['state_name', 'state_code'])
            else:
                state_list = frappe.get_all('State', filters={ 'country_name':country_name }, fields=['state_name', 'state_code'])
            if len(state_list)>0:
                response('Data get sucessfully', state_list, 200)
            else:
                response('Data not found', [], 400)
        else:
            response('Country with Country Code '+ country_code +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_state", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_district(state_code, district_name=None):
    '''
        Method to get District in given state
        args:
            state_code : State Code of State
    '''
    try:
        if frappe.db.exists('State', { 'state_code': state_code }):
            state_name = frappe.db.get_value('State', { 'state_code': state_code })
            if district_name:
                district_list = frappe.get_all('District', filters={ 'state':state_name, 'district_name': ['like', '%' + district_name + '%' ] }, fields=['district_name', 'district_code'])
            else:
                district_list = frappe.get_all('District', filters={ 'state':state_name }, fields=['district_name', 'district_code'])
            if len(district_list)>0:
                response('Data get sucessfully', district_list, 200)
            else:
                response('Data not found', [], 400)
        else:
            response('State with State Code '+ state_code +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_district", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_taluk(district_code, taluka_name=None):
    '''
        Method to get Taluk in given District
        args:
            district_code : District Code of District
    '''
    try:
        if frappe.db.exists('District', { 'district_code': district_code }):
            district_name = frappe.db.get_value('District', { 'district_code': district_code })
            if taluka_name:
                taluk_list = frappe.get_all('TalukaTahsil', filters={ 'district':district_name, 'tahsil__taluka': ['like', '%' + taluka_name + '%' ] }, fields=['tahsil__taluka as taluka_name', 'name as taluk_code'])
            else:
                taluk_list = frappe.get_all('TalukaTahsil', filters={ 'district':district_name }, fields=['tahsil__taluka as taluka_name', 'name as taluk_code'])
            if len(taluk_list)>0:
                response('Data get sucessfully', taluk_list, 200)
            else:
                response('Data not found', [], 400)
        else:
            response('District with District Code '+ district_code +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_taluk", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_religions():
    '''
        Method to get Religions
    '''
    try:
        religion_list = []
        religions = ['Buddhism','Christian','Hindu','Islam','Jain','Sikh','Others']
        for religion in religions:
            religion_list.append({'religion_name':religion, 'religion_code':religion })
        response('Data get sucessfully', religion_list, 200)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_religions", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def upload_file(from_camera=0):
    '''
        API to upload File
        args:
            attachment : sent file in form data inside Body
    '''
    try:
        if from_camera not in ['0', 0 ]:
            from_camera = 1
        else:
            from_camera = 0
        files = frappe.request.files
        file = []
        if 'attachment' in files:
            file = files['attachment']
            content = file.stream.read()
            filename = file.filename
            if 'attachment' in files and file:
                attachment = frappe.get_doc(
                    {
                        "doctype": "File",
                        "file_name": filename,
                        "content": content,
                    }
                )
                attachment.save(ignore_permissions=True)

                if (attachment.file_size > 2000000) and (from_camera==0):
                    frappe.db.rollback()
                    return response('File size exceeded the maximum allowed size of 2MB!', {}, 400)
                else:
                    frappe.db.commit()
                    return response('File uploaded sucessfully', { 'file_name': attachment.file_name, 'file_url': attachment.file_url }, 201)
        response('File is missing', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: upload_file", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def attach_file_to_doc(file_url, reference_doctype, reference_docname, reference_field=None):
    '''
        API for Attach existing file to any document
        args:
            file_url : File Url of existing File
            reference_doctype : Doctype Name
            reference_docname : Document Name
            reference_field : name of field which attachment is atttached
    '''
    try:
        if not frappe.db.exists('DocType', reference_doctype):
            return response('Invalid Reference DocType', {}, 400)
        if not frappe.db.exists(reference_doctype, reference_docname):
            return response('Invalid Reference Docname', {}, 400)
        if frappe.db.exists('File', { 'file_url':file_url }):
            file_doc = frappe.db.get_value('File', { 'file_url':file_url })
            frappe.db.set_value('File', file_doc, 'attached_to_doctype', reference_doctype)
            frappe.db.set_value('File', file_doc, 'attached_to_name', reference_docname)
            if reference_field:
                if not frappe.db.exists('DocField', { 'parent':reference_doctype, 'fieldname':reference_field, 'fieldtype': ['in', ['Attach', 'Attach Image']] }):
                    return response('Invalid Reference Field', {}, 400)
                else:
                    frappe.db.set_value(reference_doctype, reference_docname, reference_field, file_url)
            frappe.db.commit()
            return response('File Linked sucessfully', {}, 200)
        else:
            return response('File not found', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: attach_file_to_doc", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def textile_registration(category_b, first_name, middle_name, last_name, gender, date, religion, caste_category, address_line1, address_line2, address_line3, state, district, tahsil_taluka, pincode, mobile_number, email_id, entity_full_name, udyog_aadhar, njb_regi_no = None, townvillage=None):
    '''
        API for Textile Registration
        args:
            category_b : Category Name of Applicant
            first_name : First Name of Applicant
            middle_name : Middle Name of Applicant
            last_name : Last Name of Applicant
            gender : Gender of Applicant
            date : Date of Applicant
            religion : Religion of Applicant
            caste_category : Caste Category of Applicant
            address_line1 : Address Line1 of Applicant
            address_line2 : Address line2 of Applicant
            address_line3 : Address line3 of Applicant
            state : State of Applicant
            district : District of Applicant
            tahsil_taluka : Tahsil/Taluka of Applicant
            pincode : Pincode of Applicant
            mobile_number : Mobile Number of Applicant
            email_id : Email Id of Applicant
            njb_regi_no: NJB Registration Number
            entity_full_name : Entity Full Name
            townvillage : Town Village
    '''
    try:
        if mobile_number:
            religions = ['Hindu', 'Islam', 'Christian', 'Sikh', 'Buddhism', 'Jain', 'Others']
            if not frappe.db.exists('Jute Mark India Registration form', { 'mobile_number':mobile_number }):
                registration_doc = frappe.new_doc("Jute Mark India Registration form")
                if category_b not in ['Artisan', 'Manufacturer', 'Retailer']:
                    error_message = "Select Proper Category. Example: 'Artisan', 'Manufacturer', 'Retailer'"
                    if isinstance(error_message, tuple):
                        error_message = ' '.join(error_message)
                    message_parts = error_message.split('. Example: ')
                    return response(message_parts[0], {'example': message_parts[1]}, 400)
                elif gender and (gender not in ['Male','Female', 'Other']):
                    error_message = "Select Proper Gender. Example: 'Male', 'Female', 'Other'"
                    if isinstance(error_message, tuple):
                        error_message = ' '.join(error_message)
                    message_parts = error_message.split('. Example: ')
                    return response(message_parts[0], {'example': message_parts[1]}, 400)
                elif state and (not frappe.db.exists('State', state)):
                    return response('Invalid State selected', {}, 400)
                elif district and (not frappe.db.exists('District', district)):
                    return response('Invalid District selected', {}, 400)
                elif tahsil_taluka and (not frappe.db.exists('TalukaTahsil', tahsil_taluka)):
                    return response('Invalid TalukaTahsil selected', {}, 400)
                elif pincode and (not frappe.db.exists('Pincode', pincode)):
                    return response('Invalid Pincode selected', {}, 400)
                elif religion and (religion  not in religions):
                    return response('Invalid Religion selected', {}, 400)
                elif udyog_aadhar and not validate_udayam_adhar(udyog_aadhar):
                    error_message = 'Enter the Correct Format Of Udyog Aadhar. Example: UDAYAM-KR-07-0000000'
                    message_parts = error_message.split('. Example: ')
                    return response(message_parts[0], {'example': message_parts[1]}, 400)
                elif njb_regi_no and not validate_njb_number(njb_regi_no):
                    error_message = 'Enter the Correct Format Of NGB Register Number. Example: NJB00XXX000000000'
                    message_parts = error_message.split('. Example: ')
                    return response(message_parts[0], {'example': message_parts[1]}, 400)
                elif njb_regi_no and frappe.db.exists("Jute Mark India Registration form",{'njb_regi_no':njb_regi_no}):
                    return response('Already registed with this NJB Registration Number', {}, 400)
                else:
                    if entity_full_name:
                        registration_doc.set('entity_full_name', entity_full_name)
                    elif registration_doc.category_b in ['Retailer', 'Manufacturer']:
                        return response('Entity Full Name is Mandatory!', {}, 400)
                    if udyog_aadhar:
                        registration_doc.set('udyog_aadhar', udyog_aadhar)
                    elif registration_doc.category_b in ['Retailer', 'Manufacturer']:
                        return response('Udyog Aadhar is Mandatory!', {}, 400)
                    if townvillage:
                        registration_doc.set('townvillage', townvillage)
                    registration_doc.update({
                        'category_b': category_b,
                        'applicant_name': first_name,
                        'middle_name': middle_name,
                        'last_name': last_name,
                        'gender': gender,
                        'date': getdate(date),
                        'religion': religion,
                        'category__scst_other_in_case_b_is_1': caste_category,
                        'address_line_1': address_line1,
                        'address_line_2': address_line2,
                        'address_line_3': address_line3,
                        'state': state,
                        'district': district,
                        'tahsil__taluka': tahsil_taluka,
                        'pin_code': pincode,
                        'mobile_number': mobile_number,
                        'email_id': email_id,
                        'njb_regi_no': njb_regi_no,
                        'udyog_aadhar': udyog_aadhar,
                        'entity_full_name': entity_full_name
                    })
                    registration_doc.flags.ignore_mandatory = True
                    registration_doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    data = registration_doc.as_dict()
                    data['application_id'] = registration_doc.name
                    data.pop('name')
                    return response('Registered  sucessfully', data, 201)
            else:
                return response('Already Registered with this Mobile Number ', {}, 400)
        else:
            return response('Mobile Number is Mandatory!', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: textile_registration", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_file_detail(reference_doctype, reference_docname, reference_field):
    '''
        API to get file from ERP
        args:
            reference_doctype : Doctype Name
            reference_docname : Document Name
            reference_field : name of field which attachment is atttached
    '''
    try:
        if not frappe.db.exists('DocType', reference_doctype):
            return response('Invalid Reference DocType', {}, 400)
        if not frappe.db.exists(reference_doctype, reference_docname):
            return response('Invalid Reference Docname', {}, 400)
        meta = frappe.get_meta(reference_doctype)
        if not meta.has_field(reference_field):
            return response('Fieldname is Invalid', {}, 400)
        if frappe.db.get_value(reference_doctype, reference_docname, reference_field):
            file_url = frappe.db.get_value(reference_doctype, reference_docname, reference_field)
            return response('Document get successfully', file_url, 200)
        else:
            return response('Document not attached yet', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_file_detail", message=frappe.get_traceback())
        return response(exception, {}, 400)

def get_application_data(mobile_number=None, application_id=None, assigned_to=None):
    # get application data for given application_id or mobile_number
    filter = {}
    if application_id:
        filter = application_id
    elif mobile_number:
        filter = {'mobile_number':mobile_number}

    if not frappe.db.exists('Jute Mark India Registration form', filter):
        return response('No Registration form exist with this Mobile Number / Application ID', {}, 400)
    else:
        doc = frappe.get_doc('Jute Mark India Registration form', filter)
        data = doc.as_dict()
        data['application_id'] = doc.name
        data.pop('name')
        data['signature'] = None
        data['on_site_verification_form'] = None
        data['allocated_labels_count'] = 0
        fees_filter = { "category": doc.category_b, "fees_description": "New Registration"}

        # application renewal and it's sites
        data["application_renewal"] = ""
        data["application_renewal_sites"] = []
        if doc.application_renewal:
            app_renewal = frappe.db.get_value("Application Renewal", {"application_no": doc.name}, "name")
            if app_renewal:
                fees_filter["fees_description"] = "Renewal"
                data["application_renewal"] = app_renewal
                data["application_renewal_sites"] = get_site_visit_details(doc.name, assigned_to=None, doctype="Application Renewal", docname=app_renewal)

        # fees amount
        fees_amt = frappe.db.get_value("Fees Records", fees_filter, "amount") or 0
        data["amount"] = fees_amt

        # appeal and it's sites
        data["jmi_appeal"] = ""
        data["jmi_appeal_sites"] = []
        jmi_appeal = frappe.db.get_value("JMI Appeal", {"application_no": doc.name}, "name")
        if jmi_appeal:
            data["jmi_appeal"] = jmi_appeal
            data["jmi_appeal_sites"] = get_site_visit_details(doc.name, assigned_to=None, doctype="JMI Appeal", docname=jmi_appeal)
        if get_site_visit_details(doc.name):
            data.pop('textile_details_of_production_units_or_retailer_sales_outlets')
            if assigned_to:
                data['textile_details_of_production_units_or_retailer_sales_outlets'] = get_site_visit_details(doc.name, assigned_to)
            else:
                data['textile_details_of_production_units_or_retailer_sales_outlets'] = get_site_visit_details(doc.name)
        if get_on_site_verification_form(doc.name):
            on_site_verification_form = get_on_site_verification_form(doc.name)
            data['on_site_verification_form'] = on_site_verification_form
            data['signature'] = frappe.db.get_value('On-Site Verification Form', on_site_verification_form, 'signature_with_name')
            data['allocated_labels_count'] = frappe.db.get_value('On-Site Verification Form', on_site_verification_form, 'no_of_labels')
            data['label_enhancement'] = frappe.db.get_value('On-Site Verification Form', on_site_verification_form,'label_enhancement')
            if data['label_enhancement']:
                data['label_enhancement_site_visit'] = get_site_visit_details_enhancement(doc.name,data['label_enhancement'])
                data['no_of_label_requested'] = frappe.db.get_value('On-Site Verification Form', on_site_verification_form,'no_of_label_requested')
                data['no_of_label_approved'] = frappe.db.get_value('On-Site Verification Form', on_site_verification_form,'no_of_label_approved')
        data['able_to_create_appeal'] = is_able_to_create_appeal(doc.name)
        data['able_to_create_escalation'] = is_able_to_create_escalation(doc.name)
        data['no_child_labor'] = doc.no_child_labor_emp_mfg_product
        data['no_hazardous_chemical'] = doc.no_hazardous_chemical_used_mfg_product
        roles = frappe.get_roles(frappe.session.user)
        role = None
        if frappe.session.user == 'Guest':
            role='Guest'
        elif 'JMI User' in roles:
            role = 'JMI User'
        elif 'Verification Officer(VO)' in roles:
            role = 'Verification Officer(VO)'
        data['role'] = role
        data['is_paid'] = doc.is_paid
        return response('Record get successfully', data, 200)

@frappe.whitelist(allow_guest=True)
def get_application_by_user(mobile_number, assigned_to=None):
    '''
        API to get entire application by mobile_number
        args:
            mobile_number: Users mobile_number
            assigned_to: VO User ID
    '''
    try:
        return get_application_data(mobile_number=mobile_number, assigned_to=assigned_to)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_application_by_user", message=frappe.get_traceback())
        return response(exception, {}, 400)


@frappe.whitelist(allow_guest=True)
def get_application_by_id(application_id, assigned_to=None):
    '''
        API to get entire application by mobile_number
        args:
            application_id: Document name of Jute Mark India Registration Form
            assigned_to: VO User ID
    '''
    try:
        return get_application_data(application_id=application_id, assigned_to=assigned_to)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_application_by_id", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_application_details(application_id, gender, date, religion, caste_category, address_line1, address_line2, address_line3, state, district, tahsil_taluka, pincode, njb_regi_no, proof_of_address, aadhar_number, udyog_aadhar, gst_number, pan_number, i_agree=0, first_name=None, middle_name=None, last_name=None, entity_full_name=None, townvillage=None, verified_details_of_product=0, production_units_verified=0, production_in_previous_year_verified=0, procurement_in_previous_year_verified=0, attach_sample_report=0,no_child_labor_emp_mfg_product=0, no_hazardous_chemical_used_mfg_product = 0,identification_proof_is=None):
    '''
        API to get entire application by mobile_number
        args:
            application_id : JMI Application Number
            gender : Gender of Applicant
            date : Date of Applicant
            religion : Religion of Applicant
            caste_category : Caste Category of Applicant
            address_line1 : Address Line1 of Applicant
            address_line2 : Address line2 of Applicant
            address_line3 : Address line3 of Applicant
            state : State of Applicant
            district : District of Applicant
            tahsil_taluka : Tahsil/Taluka of Applicant
            pincode : Pincode of Applicant
            njb_regi_no: NJB Registration Number
            proof_of_address: Proof of Address
            aadhar_number : Aadhar Number
            udyog_aadhar : Udyog Aadhar
            gst_number : GST Number
            pan_number : PAN Number
            i_agree: 0 or 1
            first_name : First Name of Applicant
            middle_name : Middle Name of Applicant
            last_name : Last Name of Applicant
            entity_full_name : Entity Full Name
            townvillage : Town Village
            production_in_previous_year_verified: 0 or 1
            attach_sample_report: 0 or 1
            no_child_labor_emp_mfg_product:0 or 1
            no_hazardous_chemical_used_mfg_product : 0 or 1
            identification_proof_is: Identification Prood Type
    '''
    try:
        religions = ['Hindu', 'Islam', 'Christian', 'Sikh', 'Buddhism', 'Jain', 'Others']
        identification_proofs = ['Aadhaar Card', 'Driving License', 'Election Commission ID Card', 'Other government issued ID card', 'Passport']
        if frappe.session.user == 'Guest':
            return response('Guest user not allowed to update Registration, Please Login again!', {}, 400)
        if frappe.db.exists('Jute Mark India Registration form', application_id):
            registration_doc = frappe.get_doc("Jute Mark India Registration form", application_id)
            if gender and (gender not in ['Male','Female', 'Other']):
                error_message = "Select Proper Gender. Example: 'Male', 'Female', 'Other'"
                if isinstance(error_message, tuple):
                    error_message = ' '.join(error_message)
                message_parts = error_message.split('. Example: ')
            elif state and (not frappe.db.exists('State', state)):
                return response('Invalid State selected', {}, 400)
            elif district and (not frappe.db.exists('District', district)):
                return response('Invalid District selected', {}, 400)
            elif tahsil_taluka and (not frappe.db.exists('TalukaTahsil', tahsil_taluka)):
                return response('Invalid TalukaTahsil selected', {}, 400)
            elif pincode and (not frappe.db.exists('Pincode', pincode)):
                return response('Invalid Pincode selected', {}, 400)
            elif religion and (religion  not in religions):
                return response('Invalid Religion selected', {}, 400)
            elif aadhar_number and not validate_aadhar_number(aadhar_number):
                return response('Invalid Aadhar Number', {}, 400)
            elif aadhar_number  and frappe.db.exists("Jute Mark India Registration form",{'name':['!=',application_id] ,'aadhar_number':aadhar_number}):
                return response('Already registed with this Aadhar Number', {}, 400)
            elif gst_number and not validate_gst_number(gst_number):
                return response('Invalid GST Number', {}, 400)
            elif gst_number and frappe.db.exists("Jute Mark India Registration form",{'name':['!=',application_id] ,'gst_number':gst_number}):
                return response('Already registed with this GST Number', {}, 400)
            elif pan_number and not validate_pan_number(pan_number):
                return response('Invalid PAN Number', {}, 400)
            elif pan_number and frappe.db.exists("Jute Mark India Registration form",{'name':['!=',application_id],'pan_number':pan_number}):
                    return response('Already registed with this PAN Number', {}, 400)
            elif udyog_aadhar and not validate_udyog_aadhar(udyog_aadhar):
                return response('Enter the Correct Format Of Udyog Aadhar', {}, 400)
            elif udyog_aadhar and frappe.db.exists("Jute Mark India Registration form",{'name':['!=',application_id],'udyog_aadhar':udyog_aadhar}):
                    return response('Already registed with this Udyog Aadhar Number', {}, 400)
            elif njb_regi_no and not validate_njb_number(njb_regi_no):
                return response('Invalid NJB Registration Number', {}, 400)
            elif njb_regi_no and frappe.db.exists("Jute Mark India Registration form",{'name':['!=',application_id],'njb_regi_no':njb_regi_no}):
                    return response('Already registed with this NJB Registration Number', {}, 400)
            elif identification_proof_is and identification_proof_is not in identification_proofs:
                return response('Identification Proof is Invalid', {}, 400)
            else:
                if i_agree not in [0, '0']:
                    i_agree = 1
                else:
                    i_agree = 0
                if production_in_previous_year_verified not in [0, '0']:
                    production_in_previous_year_verified = 1
                else:
                    production_in_previous_year_verified = 0
                if attach_sample_report not in [0, '0']:
                    attach_sample_report = 1
                else:
                    attach_sample_report = 0
                if no_child_labor_emp_mfg_product not in [0, '0']:
                    no_child_labor_emp_mfg_product = 1
                else:
                    no_child_labor_emp_mfg_product = 0
                if no_hazardous_chemical_used_mfg_product not in [0, '0']:
                    no_hazardous_chemical_used_mfg_product = 1
                else:
                    no_hazardous_chemical_used_mfg_product = 0
                raw_data = {}
                if first_name:
                    raw_data.update({'applicant_name': first_name})
                if middle_name:
                    raw_data.update({'middle_name': middle_name})
                if last_name:
                    raw_data.update({'last_name': last_name})
                if entity_full_name:
                    raw_data.update({'entity_full_name': entity_full_name})
                if townvillage:
                    raw_data.update({'townvillage': townvillage})
                registration_doc.update(raw_data)
                registration_doc.update({
                    'gender': gender,
                    'date': getdate(date),
                    'religion': religion,
                    'category__scst_other_in_case_b_is_1': caste_category,
                    'address_line_1': address_line1,
                    'address_line_2': address_line2,
                    'address_line_3': address_line3,
                    'state': state,
                    'district': district,
                    'tahsil__taluka': tahsil_taluka,
                    'pin_code': pincode,
                    'njb_regi_no': njb_regi_no,
                    'proof_of_address': proof_of_address,
                    'aadhar_number': aadhar_number,
                    'udyog_aadhar': udyog_aadhar,
                    'pan_number': pan_number,
                    'gst_number': gst_number,
                    'i_agree': i_agree,
                    'production_in_previous_year_verified': production_in_previous_year_verified,
                    'attach_sample_report': attach_sample_report,
                    'no_child_labor_emp_mfg_product': no_child_labor_emp_mfg_product,
                    'no_hazardous_chemical_used_mfg_product': no_hazardous_chemical_used_mfg_product,
                    'identification_proof_is': identification_proof_is
                })
            registration_doc.flags.ignore_mandatory = True
            registration_doc.save(ignore_permissions=True)
            frappe.db.commit()
            data = registration_doc.as_dict()
            data['application_id'] = registration_doc.name
            data.pop('name')
            return response('Record updated successfully', data, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(application_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_application_details", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def set_android_version(version):
    '''
        API to set latest version of application to ERP
        args:
            version : Latest version of application
    '''
    try:
        if version:
            doc = frappe.get_doc('Android App Settings')
            doc.latest_version = version
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            return response('Version Succesfully updated to ERP', { 'latest_version':version }, 200)
        else:
            return response('Version is required!', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: set_android_version", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def check_for_updates(current_version):
    '''
        API to check wether updates are available or not
        args:
            current_version : current version of application
    '''
    try:
        if current_version:
            latest_version = frappe.db.get_single_value('Android App Settings', 'latest_version')
            if latest_version:
                if latest_version != current_version:
                    return response('New updates are available.', { 'latest_version':latest_version, 'current_version':current_version }, 200)
                else:
                    return response('Your app is already up to date.', { 'latest_version':latest_version, 'current_version':current_version }, 200)
            else:
                return response('Latest version is not updated to ERP!', {}, 400)
        else:
            return response('Current version is required to check Updates!', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: check_for_updates", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def label_entitlement(application_no, alloted_labels):
    '''
        API for label entitlement
        args:
            application_no : Application Number of Jute Mark India Registration form
            alloted_labels : Total no of labels alloted for an year
    '''
    try:
        if frappe.db.exists('Jute Mark India Registration form', application_no):
            workflow_state = frappe.db.get_value('Jute Mark India Registration form', application_no, 'workflow_state')
            on_site_verification_form = get_on_site_verification_form(application_no)
            if on_site_verification_form:
                doc = frappe.get_doc('On-Site Verification Form', on_site_verification_form)
                if alloted_labels:
                    if not validate_label_count(int(alloted_labels or 0)):
                        return response('Alloted Labels count should be multiple of 10!', {}, 400)
                    else:
                        frappe.db.set_value('On-Site Verification Form', on_site_verification_form, 'no_of_labels', alloted_labels)
                        frappe.db.commit()
                        return response('Labels alloted Successfully', { 'alloted_labels':alloted_labels, 'application_no':application_no, 'status':workflow_state }, 200)
                return response('Alloted Labels count should be multiple of 10', { }, 400)
            else:
                return response('Application is still Pending. Please contact Regional Officer.', { 'application_no':application_no, 'status':workflow_state }, 400)
        else:
            return response('No Applications found against this Application No', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: label_entitlement", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def label_enhancement(application_no, enhancement_type, expected_labels, reason):
    '''
        API to check wether updates are available or not
        args:
            application_no : Application Number of Jute Mark India Registration form
            enhancement_type : Enhancement Type will be Temporary/Permanent
            expected_labels : Total no of labels expected for an year
            reason : Reason for Label Enhancement
    '''
    try:
        if frappe.db.exists('Jute Mark India Registration form', application_no):
            workflow_state = frappe.db.get_value('Jute Mark India Registration form', application_no, 'workflow_state')
            on_site_verification_form = get_on_site_verification_form(application_no)
            if on_site_verification_form:
                if enhancement_type not in ['Temporary', 'Permanent']:
                    return response('Enhancement Type should be Temporary or Permanent', {}, 400)
                else:
                    no_of_labels = frappe.db.get_value("On-Site Verification Form", on_site_verification_form, "no_of_labels")
                    if not expected_labels:
                        return response('Expected Labels count should be multiple of 10!', {}, 400)
                    elif int(expected_labels or 0) < int(no_of_labels or 0):
                        return response('Required no. of Labels is less than current label count!', {}, 400)
                    else:
                        if validate_label_count(int(expected_labels or 0)):
                            doc = frappe.new_doc('Label Enhancement')
                            doc.application_no = application_no
                            doc.on_site_verification = on_site_verification_form
                            doc.label_type = enhancement_type
                            doc.required_no_of_labels = int(expected_labels or 0)
                            doc.reason_for_enhancement = reason
                            doc.user_id = frappe.db.get_value('Jute Mark India Registration form', application_no, 'email_id')
                            doc.workflow_status = 'Pending'
                            doc.save(ignore_permissions=True)
                            frappe.db.commit()
                            return response('You requested for label enhancement successfully', { 'application_no':application_no, 'status':workflow_state }, 200)
                        else:
                            return response('Expected Labels count should be multiple of 10!', {}, 400)
            else:
                return response('Application is still Pending. Please contact Regional Officer.', { 'application_no':application_no, 'status':workflow_state }, 400)
        else:
            return response('No Applications found against this Application No!', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: label_enhancement", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def validate_label_count(count):
    '''
        Method to validate the count of any labels
        count: Count of labels
    '''
    validated = False
    if count:
        if not count%10:
            validated = True
    return validated

@frappe.whitelist(allow_guest = True)
def appeal_for_rejection(data=None):
    '''
        Method to create JMI Appeal for Rejection
    '''
    data = json.loads(frappe.request.data)
    try:
        if frappe.db.exists('Jute Mark India Registration form', data.get('application_no')):
            workflow_state, last_modified = frappe.db.get_value(
                'Jute Mark India Registration form',data.get('application_no'),
                ['workflow_state', 'modified']
            )
            if workflow_state in ['Rejected by HO', 'Rejected by RO']:
                if not frappe.db.exists('JMI Appeal', {
                        'application_no':data.get('application_no'),
                        'appeal_type':'Appeal for Rejection'
                    }):
                    if not getdate(today()) >= getdate(add_to_date(getdate(last_modified), days=15)):
                        jmi_appeal_doc = frappe.new_doc('JMI Appeal')
                        jmi_appeal_doc.update({
                            'application_no': data.get('application_no'),
                            'appeal_type': 'Appeal for Rejection',
                            'workflow_state': "Draft",
                            'appealing_date': today(),
                            'no_of_labels': data.get("no_of_labels"),
                            'no_of_label_requested': data.get("no_of_label_requested"),
                            'application_remarks': data.get("application_remarks"),
                            'labels_balance': data.get("labels_balance")
                        })
                        jmi_appeal_doc.save(ignore_permissions=True)
                        jmir_doc = frappe.get_doc("Jute Mark India Registration form", jmi_appeal_doc.application_no)
                        for row in jmir_doc.textile_details_of_production_units_or_retailer_sales_outlets:
                            if row.approve == 1:
                                row.approve = 0
                            if row.reject == 1:
                                row.reject = 0
                        for row in jmir_doc.textile_details_of_product:
                            if row.approve == 1:
                                row.approve = 0
                            if row.reject == 1:
                                row.reject = 0
                        jmir_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                        frappe.db.set_value("JMI Appeal", jmi_appeal_doc.name, "workflow_state", "Pending")
                        frappe.db.commit()
                        jmi_appeal_doc.workflow_state = "Pending"
                        return response('Successfully created Appeal for Rejection', { 'jmi_appeal_doc':jmi_appeal_doc }, 201)
                    else:
                        return response('Appealing date is Over. Should Create within 15 Days!', { 'application_no':data.get('application_no'), 'status':workflow_state }, 400)
                else:
                    return response('Appeal is already created against this Application No.', { 'application_no':data.get('application_no'), 'status':workflow_state }, 400)
            else:
                return response('Application is in \'{0}\' Status.'.format(workflow_state), { 'application_no':data.get('application_no'), 'status':workflow_state }, 400)
        else:
            return response('No Applications found against this Application No!', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: appeal_for_rejection", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest = True)
def appeal_for_escalation(data=None):
    '''
        Method to create JMI Appeal for Escalation
    '''
    data = json.loads(frappe.request.data)
    try:
        if frappe.db.exists('JMI Appeal', data.get('jmi_appeal')):
            application_no, previous_appealing_date = frappe.db.get_value(
                'JMI Appeal', data.get('jmi_appeal'), ['application_no', 'appealing_date'])
            workflow_state = frappe.db.get_value('Jute Mark India Registration form', application_no, 'workflow_state')
            if not frappe.db.exists('JMI Appeal', {
                'jmi_appeal': data.get('jmi_appeal'),
                'appeal_type':'Appeal for Escalation'
                }):
                if not getdate(today()) < getdate(add_to_date(getdate(previous_appealing_date), days=10)):
                    jmi_appeal_doc = frappe.new_doc('JMI Appeal')
                    jmi_appeal_doc.update({
                        'application_no': application_no,
                        'workflow_state': "Draft",
                        'appealing_date': today(),
                        'jmi_appeal': data.get('jmi_appeal'),
                        'appeal_type': 'Appeal for Escalation',
                        'no_of_labels': data.get("no_of_labels"),
                        'no_of_label_requested': data.get("no_of_label_requested"),
                        'application_remarks': data.get("application_remarks"),
                        'labels_balance': data.get("labels_balance")
                    })
                    jmi_appeal_doc.save(ignore_permissions = True)
                    frappe.db.commit()
                    frappe.db.set_value("JMI Appeal", jmi_appeal_doc.name, "workflow_state", "Pending")
                    frappe.db.commit()
                    jmi_appeal_doc.workflow_state = "Pending"
                    return response('Appeal escalate successfully', {'appeal_id':jmi_appeal_doc.name, 'application_no':application_no, 'status':workflow_state} ,201)
                else:
                    return response('Appeal for Escalation can only be created after 10 Days of Appeal!', {'application_no':application_no, 'status':workflow_state}, 401)
            else:
                return response('Appeal for escalation is already created against this Application No.', {'application_no':application_no, 'status':workflow_state}, 401)
        else:
            return response('JMI Appeal \'{0}\' not found!'.format(data.get('jmi_appeal')), {}, 401)
    except Exception as exception:
        frappe.log_error(title="Mobile API: appeal_for_escalation", message=frappe.get_traceback())
        return response(exception, {}, 401)

@frappe.whitelist(allow_guest = True)
def get_labels(application_no):
    '''
        Method to get labels from Jute Mark India Registration Form
        application_no: Application Number of Jute Mark India Registration Form
    '''
    try:
        if frappe.db.exists('Jute Mark India Registration form', application_no):
            workflow_state = frappe.db.get_value('Jute Mark India Registration form', application_no, 'workflow_state')
            on_site_verification_form = get_on_site_verification_form(application_no)
            if on_site_verification_form:
                doc = frappe.get_doc('On-Site Verification Form', on_site_verification_form)
                if doc.no_of_labels:
                    return response('Get data successfully', {'application_no':application_no, 'status':workflow_state, 'date':doc.date, 'alloted_labels':doc.no_of_labels }, 200)
                else:
                    return response('Labels not allocated yet. Please contact Regional Officer!', { 'application_no':application_no, 'status':workflow_state }, 400)
            else:
                return response('Labels not allocated yet. Please contact Regional Officer!', { 'application_no':application_no, 'status':workflow_state }, 400)
        else:
            return response('No Applications found against this Application No!', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_labels", message=frappe.get_traceback())
        return response(exception, {}, 400)


@frappe.whitelist(allow_guest=True)
def get_on_site_verification_form(application_no):
    '''
        Method to get on site verification form from application_no
        application_no: Jute Mark India Registration Form
    '''
    on_site_verification_form = False
    if frappe.db.exists('On-Site Verification Form', {'textile_registration_no': application_no}):
        on_site_verification_form = frappe.db.get_value('On-Site Verification Form', {
            'textile_registration_no': application_no
        }, "name")
    return on_site_verification_form

@frappe.whitelist(allow_guest=True)
def add_new_device(user, device_token):
    '''
        Method to add device token of a user to the database
        args:
            user : email of the user
            device_token : device token of the device logging in from
    '''
    if user and device_token:
        if not frappe.db.exists('User Device', { 'user':user, 'device_id':device_token }):
            new_device = frappe.new_doc('User Device')
            new_device.user = user
            new_device.device_id = device_token
            new_device.save(ignore_permissions=True)
            frappe.db.commit()

@frappe.whitelist(allow_guest=True)
def signup(email_id, mobile_number):
    '''
        Method to add device token of a user to the database
        args:
            email_id : email of the user
            mobile_number : mobile_number of the user
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", { 'email_id':email_id }):
            return response('User already exists with this Email!', {}, 400)
        if frappe.db.exists("Jute Mark India Registration form", { 'mobile_number':mobile_number }):
            return response('User already exists with this Mobile Number!', {}, 400)
        register(email_id, mobile_number)
        frappe.db.commit()
        frappe.clear_messages()
        return response('Verification code send to mail successfully', {}, 201)
    except Exception as exception:
        frappe.log_error(title="Mobile API: signup", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def verify_signup_otp(mobile_number, otp):
    '''
        Method to add device token of a user to the database
        args:
            mobile_number : mobile_number of the user
            otp : OTP recieved via email
    '''
    try:
        if not frappe.db.exists("User Registration", { 'mobile_number':mobile_number }):
            return response('User does not exists with this Mobile Number. Please signup first!', {}, 400)
        otp_validated = verify_otp(mobile_number, otp)
        frappe.db.commit()
        frappe.clear_messages()
        if otp_validated:
            return response('OTP verified Successfully', {}, 200)
        else:
            return response('Invalid OTP. Please check again!', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: verify_signup_otp", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_pincode(district, pin_code=None):
    '''
        Method to get Pincodes in given District
        args:
            district : Name of District
            pin_code : Pincode
    '''
    try:
        if frappe.db.exists('District', district):
            if pin_code:
                pin_code_list = frappe.get_all('Pincode', filters={ 'district':district, 'name': ['like', '%' + pin_code + '%' ] }, fields=['name as pin_code'])
            else:
                pin_code_list = frappe.get_all('Pincode', filters={ 'district':district }, fields=['name as pin_code'])
            if len(pin_code_list)>0:
                response('Data get sucessfully', pin_code_list, 200)
            else:
                response('Data not found', [], 400)
        else:
            response('District \'{0}\' does not exist'.format(district), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_pincode", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_regional_office(district_code, regional_office=None):
    '''
        Method to get Regional Office in given State
        args:
            district_code : District Code
            regional_office : Regional Office name to search
    '''
    try:
        if frappe.db.exists('District', { 'district_code': district_code }):
            district_name = frappe.db.get_value('District', { 'district_code': district_code })
            query = '''
                SELECT
                    ro.regional_office
                FROM
                    `tabRegional Office` as ro,
                    `tabDistricts` as d
                WHERE
                    d.parent = ro.name AND
                    d.district = "{district}"
            '''.format(district=district_name)
            if regional_office:
                query += 'AND ro.name like "%{regional_office}%"'.format(regional_office=regional_office)
            regional_office_list = frappe.db.sql(query, as_dict = 1)
            if len(regional_office_list)>0:
                response('Data get sucessfully', regional_office_list, 200)
            else:
                response('Data not found', [], 400)
        else:
            response('District with District Code {0} does not exist'.format(district_code), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_regional_office", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def create_data_import(doctype, file_url):
    '''
        Method to Create Data Import
        args:
            doctype : Name of the Doctype need to Import
            file_url : file_url of the import file
    '''
    try:
        if frappe.db.exists('DocType', doctype):
            if file_url:
                if frappe.db.exists('File', { 'file_url': file_url }):
                    data_import = frappe.new_doc('Data Import')
                    data_import.reference_doctype = doctype
                    data_import.import_type = 'Insert New Records'
                    data_import.import_file = file_url
                    data_import.save(ignore_permissions=True)
                    data_import.start_import()
                    data_import_status = frappe.db.get_value('Data Import', data_import.name, 'status')
                    frappe.db.commit()
                    response('Data Import Created Succesfully', { "data_import_id":data_import.name, "doctype":doctype, "import_file":file_url, 'status':data_import_status }, 201)
                else:
                    response('Invalid File url', {}, 400)
            else:
                response('Fileurl is mandatory', {}, 400)
        else:
            response('DocType '+ doctype +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: create_data_import", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_docs(doctype, assigned_to=None):
    '''
        Method to get Documents
        args:
            doctype : Name of the Doctype
            assigned_to : User name to filter by assigned
    '''
    try:
        if frappe.db.exists('DocType', doctype):
            workflow_doctypes = [ 'Jute Mark India Registration form', 'Label Enhancement', 'Actual Site Visit Plan', 'Request For Label Fulfilment', 'On-Site Verification Form' ]
            if doctype in workflow_doctypes:
                fields=['name', 'workflow_state as status']
                fields_sql = "name, workflow_state as status"
            else:
                fields=['name']
                fields_sql = "name"
            if assigned_to:
                query = '''
                    SELECT
                        {fields}
                    FROM
                        `tab{doctype}`
                    WHERE
                        `tab{doctype}`.`_assign` like "%{user}%
                    ORDER BY
                        modified DESC
                '''.format(fields=fields_sql, doctype=doctype, user=assigned_to)
                doc_list = frappe.db.sql(query, as_dict = 1)
            else:
                doc_list = frappe.db.get_list(doctype, fields=fields)
            if len(doc_list)>0:
                response('Data get successfully', doc_list, 200)
            else:
                response('Data not found', [], 400)
        else:
            response('DocType '+ doctype +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_docs", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def create_workflow_action(doctype, docname, workflow_state):
    '''
        Method to make workflow action
        args:
            doctype : Name of the Doctype
            docname : Name of the document
            workflow_state : Next workflow action
    '''
    try:
        if frappe.session.user == 'Guest':
            return response('Guest user not allowed to update Registration, Please Login again!', {}, 400)
        if frappe.db.exists('DocType', doctype):
            if frappe.db.exists(doctype,docname):
                if not frappe.db.exists('Workflow State', workflow_state):
                    response('Workflow State ' + workflow_state +' does not exist', {}, 400)
                else:
                    workflow = get_workflow(doctype)
                    if workflow:
                        doc = frappe.get_doc(doctype, docname)
                        if doctype == 'Jute Mark India Registration form':
                            site_visit = []
                            site_v_plan=frappe.db.sql("""SELECT name from `tabActual Site Visit Plan` where application_no='{0}' and workflow_state in ('Draft', 'Pending', 'Rejected by RO')""".format(docname), as_dict=1)
                            for row in site_v_plan:
                                site_visit.append(row.get("name"))

                            if site_visit:
                                msg = 'Site visit not yet done for Site Visit id : {0}'.format(", ".join(site_visit))
                                return response(msg , {}, 400)

                            if workflow_state == 'Submitted':
                                user = frappe.session.user
                                user_roles = frappe.get_roles(user)
                                if 'Verification Officer(VO)' in user_roles:
                                    #form_doc = frappe.get_doc("Jute Mark India Registration form", docname)

                                    if not doc.tahsil__taluka:
                                        return response("Please add Tahsil/Taluka!",{},400)
                                    if not doc.townvillage:
                                        return response("Please add Town/Village!",{},400)


                                    if doc.category_b == 'Artisan':
                                        if not doc.religion:
                                            return response("Please add Religion!", {}, 400)
                                        if not doc.category__scst_other_in_case_b_is_1:
                                            return response("Please add Category!", {}, 400)
                                        if not doc.aadhar_number:
                                            return response("Please add Aadhar Number!" , {}, 400)
                                        if not doc.aadhar_card_copy:
                                            return response("Please attach Aadhar Copy!", {}, 400)
                                        if not doc.identification_proof:
                                            return response("Please add Identification_proof!", {}, 400)
                                    else:
                                        if not doc.gst_number:
                                            return response("please add GST Number!", {}, 400)
                                        if not doc.gst_copy:
                                            return response("Please attach GST Copy!", {}, 400)
                                        if not doc.pan_number:
                                            return response("Please add Pan Number!", {}, 400)
                                        if not doc.pan_card_copy:
                                            return response("Please attach PAN card Copy!", {}, 400)
                                        if not doc.udyog_aadhar:
                                            return response("Please add Udyog Aadhar Number!", {}, 400)
                                        if not doc.udyog_aadhar_copy:
                                            return response("Please attach Udyog Aadhar copy!", {}, 400)
                                        if not doc.certificate_of_registration__in_case_b_is_2_or_3:
                                            return response("Please attach certificate_of_registration!", {}, 400)

                                    if not doc.photo:
                                        return response("Please add Passport size photo!" , {}, 400)
                                    if not  doc.proof_of_address:
                                        return response("Please add Proof of Address!", {}, 400)
                                    if not doc.upload_agreement:
                                        return response("Please Upload Agreement!",{},400)
                                    for row in doc.documents:
                                        if not row.upload_test_report:
                                            return response("Please Upload Test Report in Documents Section!", {}, 400)


                                    if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':docname}):
                                        on_site_verification_doc = frappe.get_doc("On-Site Verification Form",{'textile_registration_no':docname})
                                        if not on_site_verification_doc.no_of_labels or on_site_verification_doc.no_of_labels == 0:
                                            msg = 'Please fill No of Lables in On-Site Verification Form: {0}'.format(on_site_verification_doc.name)
                                            return response(msg , {}, 400)
                                        if on_site_verification_doc.label_enhancement and on_site_verification_doc.no_of_label_approved==0:
                                            msg = 'Please Add No of Label Approved in On-Site Verification Form: {0}'.format(on_site_verification_doc.name)
                                            return response(msg , {}, 400)
                                        if on_site_verification_doc.site_visit_photos:
                                            for row in on_site_verification_doc.site_visit_photos:
                                                if not row.photograph_1 and not row.photograph_2:
                                                    msg = 'Please Add site photographs for : {0}'.format(row.actual_site_visit_plan)
                                                    return response(msg , {}, 400)
                                        if not on_site_verification_doc.signature_with_name:
                                            msg = 'Please add Signature on On-Site Verification Form: {0}'.format(on_site_verification_doc.name)
                                            return response(msg , {}, 400)

                            site_visit_details = get_primary_site_details(docname)
                            if workflow_state == 'Application Submitted':
                                if doc.category_b != 'Artisan':
                                    if not is_site_details_filled(doc.name):
                                        return response('Please fill Site Details!', {}, 400)
                                if not doc.textile_details_of_product:
                                    return response('Please fill Details of Product!', {}, 400)
                                if not doc.i_agree:
                                    return response('Please check \'I Agree\' button!', {}, 400)
                            if is_sampling_required(doc.name):
                                if not (doc.attach_sample_report  or doc.submission_of_sample_for_testing):
                                    return response("Either you need to enable \'Will You Submit Sample Report\' checkbox or \'Submission of Sample For Testing\' Table need to be filled!", {}, 400)

                            if workflow_state == 'Submitted':
                                if not site_visit_details:
                                    return response('No Primary Site found!', {}, 400)
                                else:
                                    if site_visit_details.assigned_for != frappe.session.user:
                                        return response('Only VOs allocated to the primary site can submit the application to RO!', {}, 400)
                                    if site_visit_details.workflow_state != 'Approved By RO':
                                        return response('Actual Site Visit Plan is not yet Approved for Primary Site!', {}, 400)

                        frappe.db.set_value(doc.doctype, doc.name, "workflow_state", workflow_state)
                        frappe.db.commit()
                        if doctype == 'Jute Mark India Registration form':
                            if workflow_state in ['Draft', 'Application Submitted']:
                                return response('Succesfully Registered Application', { 'name':docname, 'status':workflow_state }, 200)
                            if workflow_state == 'Assigned VO':
                                return response('Succesfully Assigned Application to VO', { 'name':docname, 'status':workflow_state }, 200)
                            response('Succesfully updated Application', { 'name':docname, 'status':workflow_state }, 200)
                        else:
                            response('Succesfully updated workflow action', { 'name':docname, 'status':workflow_state }, 200)
                    else:
                        response('Workflow does not exist for this DocType', {}, 400)
            else:
                response(doctype + ' ' + docname +' does not exist', {}, 400)
        else:
            response('DocType '+ doctype +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: create_workflow_action", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_next_workflow_actions(doctype, docname, user_id):
    '''
        Method to make workflow action
        args:
            doctype : Name of the Doctype
            docname : Name of the document
            workflow_state : Next workflow action
    '''
    try:
        if frappe.db.exists('DocType', doctype):
            if frappe.db.exists(doctype, docname):
                workflow = get_workflow(doctype)
                if workflow:
                    curent_status = frappe.db.get_value(doctype, docname, 'workflow_state')
                    query = '''
                        SELECT
                            next_state as state,
                            action,
                            allowed as role
                        FROM
                            `tabWorkflow Transition` as wt,
                            `tabWorkflow` as w
                        WHERE
                            w.name = wt.parent AND
                            w.name = "{workflow}" AND
                            wt.state = "{current_state}"
                    '''.format(workflow=workflow, current_state=curent_status)
                    data = frappe.db.sql(query, as_dict=True)
                    next_states = []
                    next_actions = []
                    roles = []
                    for row in data:
                        next_states.append(row.state)
                        next_actions.append(row.action)
                        if row.role not in roles:
                            roles.append(row.role)
                    user_roles = set(frappe.get_roles(user_id))
                    r = set(roles).intersection(user_roles)
                    if r:
                        response('Succesfully get workflow actions', {'name':docname, 'curent_status':curent_status,'next_actions':next_states, 'next_states': next_states}, 200)
                    else:
                        response('No more Workflow Action exist for this user', {}, 200)
                else:
                    response('Workflow does not exist for this DocType', {}, 400)
            else:
                response(doctype + ' ' + docname +' does not exist', {}, 400)
        else:
            response('DocType '+ doctype +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_next_workflow_actions", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_workflow(doctype):
    '''
        Method to get Active workflow of a doctype
        args:
            doctype : Name of the doctype
    '''
    workflow = False
    if frappe.db.exists('Workflow', {'is_active': 1, 'document_type': doctype }):
        workflow = frappe.db.get_value('Workflow', {'is_active': 1, 'document_type': doctype})
    return workflow


@frappe.whitelist(allow_guest=True)
def add_production_details(jmi_id, name_of_unit, address, no_of_male_artisan, no_of_female_artisan, no_of_other_artisan):
    '''
        Method to add Textile Details of Production Units or Retailer Sales Outlets
        args:
            jmi_id : Registration Number of JMI Reg form
            name_of_unit : Name of Unit / Outlet
            address : Address
            no_of_male_artisan : No of Male Artisan
            no_of_female_artisan : No of Female Artisan
            no_of_other_artisan : No of Other Artisan
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form",jmi_id):
            if not is_number(no_of_male_artisan):
                return response('No of Male Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_female_artisan):
                return response('No of Female Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_other_artisan):
                return response('No of Other Artisan should be a number greater than Zero!', {}, 400)
            jmir_doc = frappe.get_doc("Jute Mark India Registration form", jmi_id)
            if jmir_doc.category_b != 'Artisan':
                values = jmir_doc.textile_details_of_production_units_or_retailer_sales_outlets
                flag = 0
                for row in values:
                    if row.name_of_unit__outlet==name_of_unit and row.address==address:
                        flag = 1
                        break
                if flag == 0:
                    jmir_doc.append('textile_details_of_production_units_or_retailer_sales_outlets',{
                        'name_of_unit__outlet':name_of_unit,
                        'address' : address,
                        'no_of_male_artisan' : no_of_male_artisan,
                        'no_of_female_artisan' : no_of_female_artisan,
                        'no_of_other_artisan' : no_of_other_artisan
                    })
                    jmir_doc.flags.ignore_mandatory = True
                    jmir_doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    idx = len(jmir_doc.textile_details_of_production_units_or_retailer_sales_outlets) - 1
                    output = jmir_doc.textile_details_of_production_units_or_retailer_sales_outlets[idx]
                    response('Data added sucessfully', output, 201)
                else :
                    response('Same data already added!', {}, 400)
            else:
                response('Production Units can not be added for Artisan!', {}, 400)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: add_production_details", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_production_details(jmi_id):
    '''
        Method to get Textile Details of Production Units or Retailer Sales Outlets
        args:
            jmi_id: JMI Registration Id
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            output = get_site_visit_details(jmi_id)
            if len(output):
                response('Data Get sucessfully', output, 200)
            else:
                response('Data not found!', {}, 400)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_production_details", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_production_details(jmi_id, row_id, name_of_unit, address, no_of_male_artisan, no_of_female_artisan, no_of_other_artisan, approve=0, reject=0):
    '''
    Method to update Textile Details of Production Units or Retailer Sales Outlets
    args:
        jmi_id : Registration Number of JMI Reg form
        row_id : Name of Child Table
        name_of_unit : Name of Unit / Outlet
        address : Address
        no_of_male_artisan : No of Male Artisan
        no_of_female_artisan : No of Female Artisan
        no_of_other_artisan : No of Other Artisan
    '''

    try:
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Textile_Details of Production Units or Retailer Sales Outlets', row_id):
                return response('Data not found with these IDs!', {}, 400)

            if not is_number(no_of_male_artisan):
                return response('No of Male Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_female_artisan):
                return response('No of Female Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_other_artisan):
                return response('No of Other Artisan should be a number greater than Zero!', {}, 400)
            frappe.db.set_value('Textile_Details of Production Units or Retailer Sales Outlets', row_id, 'name_of_unit__outlet', name_of_unit)
            frappe.db.set_value('Textile_Details of Production Units or Retailer Sales Outlets', row_id, 'address', address)
            frappe.db.set_value('Textile_Details of Production Units or Retailer Sales Outlets', row_id, 'no_of_male_artisan', no_of_male_artisan)
            frappe.db.set_value('Textile_Details of Production Units or Retailer Sales Outlets', row_id, 'no_of_female_artisan', no_of_female_artisan)
            frappe.db.set_value('Textile_Details of Production Units or Retailer Sales Outlets', row_id, 'no_of_other_artisan', no_of_other_artisan)
            frappe.db.set_value('Textile_Details of Production Units or Retailer Sales Outlets', row_id, 'approve', int(approve or 0))
            frappe.db.set_value('Textile_Details of Production Units or Retailer Sales Outlets', row_id, 'reject', int(reject or 0))
            frappe.db.commit()
            output = get_values_from_child_table('Textile_Details of Production Units or Retailer Sales Outlets', jmi_id, row_id)

            # Update values inside Actual site visit plan
            app_doc = frappe.get_doc("Jute Mark India Registration form", jmi_id)
            for row in app_doc.textile_details_of_production_units_or_retailer_sales_outlets:
                if row.name == row_id and row.assign_to:
                    site_visit_doc = frappe.get_doc("Actual Site Visit Plan", {'application_no': app_doc.name, 'assigned_for': row.assign_to})
                    frappe.db.set_value('Actual Site Visit Plan', site_visit_doc.name, 'no_of_male_artisan', no_of_male_artisan)
                    frappe.db.set_value('Actual Site Visit Plan', site_visit_doc.name, 'no_of_female_artisan', no_of_female_artisan)
                    frappe.db.set_value('Actual Site Visit Plan', site_visit_doc.name, 'no_of_other_artisan', no_of_other_artisan)
                    frappe.db.commit()

            # Return data after updating all rows
            output = get_values_from_child_table('Textile_Details of Production Units or Retailer Sales Outlets', jmi_id, row_id)
            return response('Data updated successfully', output, 200)

        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)

    except Exception as exception:
        frappe.log_error(title="Mobile API: update_production_details", message=frappe.get_traceback())
        return response(exception, {}, 400)


@frappe.whitelist(allow_guest=True)
def delete_production_details(jmi_id, row_id):
    '''
        Method to Delete Textile Details of Production Units or Retailer Sales Outlets
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of Child Table row
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form",jmi_id):
            if not frappe.db.exists('Textile_Details of Production Units or Retailer Sales Outlets', row_id):
                return response('Data not found for this IDs!', {}, 400)
            frappe.db.delete('Textile_Details of Production Units or Retailer Sales Outlets', row_id)
            frappe.db.commit()
            return response('Production details of site deleted', {}, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_production_details", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def add_submission_of_sample(jmi_id, p_type, desc_of_product, declared_fibre_content):
    '''
        Method to add Submission of Sample For Testing
        args:
            jmi_id : Registration Number of JMI Reg form
            p_type : Product type
            desc_of_product : Description of Product
            declared_fibre_content : Declared Fibre Content
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not (is_float(declared_fibre_content) and is_jmi_percentage(declared_fibre_content)):
                return response('Fiber Content should be in Percentage >= 50%!', {}, 400)
            if not frappe.db.exists('Product Type', p_type):
                return response('Invalid Product type selected', {}, 400)
            else :
                jmir_doc = frappe.get_doc("Jute Mark India Registration form",jmi_id)
                values = jmir_doc.submission_of_sample_for_testing
                flag = 0
                for row in values:
                    if row.product_type==p_type:
                        flag = 1
                        break
                if flag == 0:
                    jmir_doc.append('submission_of_sample_for_testing',{
                        'product_type':p_type,
                        'description_of_product': desc_of_product,
                        'declared_fibre_content': declared_fibre_content
                        })
                    jmir_doc.flags.ignore_mandatory = True
                    jmir_doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    idx = len(jmir_doc.submission_of_sample_for_testing) - 1
                    output = jmir_doc.submission_of_sample_for_testing[idx]
                    response('Data added sucessfully', output, 201)
                else :
                    response('Same data already added', {}, 400)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: add_submission_of_sample", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_submission_of_sample(jmi_id, row_id, p_type, desc_of_product, declared_fibre_content):
    '''
        Method to update Submission of Sample For Testing
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of child table row
            p_type : Product type
            desc_of_product : Description of Product
            declared_fibre_content : Declared Fibre Content
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Submission of Sample For Testing', row_id):
                return response('Data not found for these IDs!', {}, 400)
            if not (is_float(declared_fibre_content) and is_jmi_percentage(declared_fibre_content)):
                return response('Fiber Content should be in Percentage >= 50%!', {}, 400)
            if not frappe.db.exists('Product Type', p_type):
                return response('Invalid Product type selected', {}, 400)
            else :
                frappe.db.set_value('Submission of Sample For Testing', row_id, 'product_type', p_type)
                frappe.db.set_value('Submission of Sample For Testing', row_id, 'description_of_product', desc_of_product)
                frappe.db.set_value('Submission of Sample For Testing', row_id, 'declared_fibre_content', declared_fibre_content)
                frappe.db.commit()
                output = get_values_from_child_table('Submission of Sample For Testing', jmi_id, row_id)
                return response('Data updated sucessfully', output, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_submission_of_sample", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def delete_submission_of_sample(jmi_id, row_id):
    '''
        Method to delete Submission of Sample For Testing
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of Child table rows
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Submission of Sample For Testing', row_id):
                return response('Data not found for these IDs!', {}, 400)
            frappe.db.delete('Submission of Sample For Testing', row_id)
            frappe.db.commit()
            return response('Data deleted sucessfully', {}, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_submission_of_sample", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_submission_of_sample(jmi_id):
    '''
        Method to add Submission of Sample For Testing
        args:
            jmi_id : Registration Number of JMI Reg form
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            jmir_doc = frappe.get_doc("Jute Mark India Registration form",jmi_id)
            if jmir_doc.submission_of_sample_for_testing:
                output = get_values_from_child_table('Submission of Sample For Testing', jmi_id)
                return response('Data get sucessfully', output, 200)
            return response('Data not found', {}, 400)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_submission_of_sample", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_detail_of_prodution_in_previous_year(jmi_id, row_id, p_type, jute_fun, p_desc, uom, produced, sold, self_consumed, remark):
    '''
        Method to update Textile Details of Production In Previous Year (Artisan / Manufacturer)
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of Child table row
            p_type : Product Type
            p_desc : Product Description
            jute_fun : Function of Jute
            uom : UOM
            produced : Produced
            sold : Sold
            self_consumed : Self Consumed
            remark : Remark
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Product Type', p_type):
                return response('Invalid Product type selected', {}, 400)
            if not frappe.db.exists('Textile_Details of Production In Previous Year', row_id):
                return response('Data not found with these IDs!', {}, 400)
            elif uom and not frappe.db.exists('JMI UOM', uom):
                return response('Invalid Units of Measurement selected', {}, 400)
            elif jute_fun and not frappe.db.exists('JMI Product Function', jute_fun):
                return response('Invalid JMI Product Function selected', {}, 400)
            elif not is_number(produced):
                return response('Produced should be a number greater than Zero!', {}, 400)
            elif not is_number(sold):
                return response('Sold should be a number greater than Zero!', {}, 400)
            elif not is_number(self_consumed):
                return response('Self Consumed should be a number greater than Zero!', {}, 400)
            elif int(produced or 0)< (int(sold or 0)+int(self_consumed or 0)):
                return response('Produced Qty should be greater than or equal to Sold+Self Consumed!', {}, 400)
            else:
                frappe.db.set_value('Textile_Details of Production In Previous Year', row_id, 'product_description', p_desc)
                frappe.db.set_value('Textile_Details of Production In Previous Year', row_id, 'function_of_jute_material_in_the_product', jute_fun)
                frappe.db.set_value('Textile_Details of Production In Previous Year', row_id, 'produced', produced)
                frappe.db.set_value('Textile_Details of Production In Previous Year', row_id, 'sold', sold)
                frappe.db.set_value('Textile_Details of Production In Previous Year', row_id, 'self_consumed', self_consumed)
                frappe.db.set_value('Textile_Details of Production In Previous Year', row_id, 'remark', remark)
                frappe.db.set_value('Textile_Details of Production In Previous Year', row_id, 'uom', uom)
                frappe.db.commit()
                output = get_values_from_child_table('Textile_Details of Production In Previous Year', jmi_id, row_id)
                return response('Data updated sucessfully', output, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API:update_detail_of_prodution_in_previous_year", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def delete_detail_of_prodution_in_previous_year(jmi_id, row_id):
    '''
        Method to delete Textile Details of Production In Previous Year (Artisan / Manufacturer)
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of Child table row
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Textile_Details of Production In Previous Year', row_id):
                return response('Data not found with these IDs!', {}, 400)
            else:
                frappe.db.delete('Textile_Details of Production In Previous Year', row_id)
                frappe.db.commit()
                return response('Data deleted successfully', {}, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_detail_of_prodution_in_previous_year", message=frappe.get_traceback())
        return response(exception, {}, 400)


@frappe.whitelist(allow_guest=True)
def update_detail_of_procrement_in_previous_year(jmi_id, row_id, p_type, p_desc, jute_fun, uom, procured, sold, stock, remark):
    '''
        Method to update Textile Detailsof Procrement In Previous Year For Retailer
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of Child table row
            p_type : Product type
            p_desc : Product Description
            jute_fun : Function of Jute
            uom : UOM
            procured : Procured
            sold : Sold
            stock : Stock
            remark : Remark
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Details Of Procurement In Previous Year For Retailers', row_id):
                return response('Data not found with these IDs!', {}, 400)
            if not frappe.db.exists('Product Type', p_type):
                return response('Invalid Product type selected', {}, 400)
            if not frappe.db.exists('JMI UOM', uom):
                return response('Invalid Units of Measurement selected', {}, 400)
            elif jute_fun and not frappe.db.exists('JMI Product Function', jute_fun):
                return response('Invalid JMI Product Function selected', {}, 400)
            if not is_number(procured):
                return response('Procured should be a number greater than Zero!', {}, 400)
            if not is_number(sold):
                return response('Sold should be a number greater than Zero!', {}, 400)
            if not is_number(stock):
                return response('Stock should be a number greater than Zero!', {}, 400)
            elif int(procured or 0)< (int(sold or 0)+int(stock or 0)):
                return response('Procured Qty should be greater than or equal to Sold+Stock!', {}, 400)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'product_type', p_type)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'function_of_jute_material_in_the_product', jute_fun)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'uom', uom)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'procured', procured)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'sold', sold)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'stock', stock)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'remark', remark)
            frappe.db.set_value('Details Of Procurement In Previous Year For Retailers', row_id, 'product_description', p_desc)
            frappe.db.commit()
            output = get_values_from_child_table('Details Of Procurement In Previous Year For Retailers', jmi_id, row_id)
            return response('Data updated sucessfully', output, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_detail_of_procrement_in_previous_year", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def delete_detail_of_procrement_in_previous_year(jmi_id, row_id):
    '''
        Method to Delete Textile Detailsof Procrement In Previous Year For Retailer
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of Child table row
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Details Of Procurement In Previous Year For Retailers', row_id):
                return response('Data not found with these IDs!', {}, 400)
            else:
                frappe.db.delete('Details Of Procurement In Previous Year For Retailers', row_id)
                frappe.db.commit()
                return response('Data deleted sucessfully', {}, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_detail_of_procrement_in_previous_year", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def add_details_of_product(jmi_id, p_type, p_desc, fiber_content, fun_jute, visiblity, test_report, package_unit,produced, self_consumed, sold, attachment=None):
    '''
        Method to add Details of Products
        args:
            jmi_id : Registration Number of JMI Reg form
            p_type : Product type
            p_desc : Product Description
            fiber_content : Fiber Content
            fun_jute : Function of jute material in the product
            visiblity : Whether Jute is Visible or Not Visible in the Product
            test_report : Test Report
            attachment : Attachment
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if not frappe.db.exists('Product Type', p_type):
                response('Invalid Product Type selected', {}, 400)
            elif fun_jute and not frappe.db.exists('JMI Product Function', fun_jute):
                response('Invalid Function of jute material in the product selected', {}, 400)
            elif visiblity not in ['Yes','No']:
                response('Visiblity should be either \'Yes\' or \'No\'', {}, 400)
            elif test_report not in ['Available','Not Available']:
                response('Test Report should be either \'Available\' or \'Not Available\'', {}, 400)
            elif not (is_float(fiber_content) and is_jmi_percentage(fiber_content)):
                return response('Fiber Content should be in Percentage >= 50%!', {}, 400)
            elif int(produced or 0)< (int(sold or 0)+int(self_consumed or 0)):
                return response('Produced Qty should be greater than or equal to Sold + Self Consumed!', {}, 400)
            else:
                jmir_doc = frappe.get_doc("Jute Mark India Registration form", jmi_id)
                flag = 0
                for row in jmir_doc.textile_details_of_product:
                    if row.product_type==p_type and row.fiber_content==float(fiber_content) and row.product_description==p_desc and row.function_of_jute_material_in_the_product==fun_jute:
                        flag = 1
                        break
                if flag == 0:
                    jmir_doc.append('textile_details_of_product',{
                        'product_type': p_type,
                        'product_description': p_desc,
                        'fiber_content': fiber_content,
                        'function_of_jute_material_in_the_product': fun_jute,
                        'whether_jute_is_visible_or_not_visible_in_the_product': visiblity,
                        'test_report_details': test_report,
                        'attachment': attachment,
                        'package_unit': package_unit,
                        'produced': produced,
                        'self_consumed': self_consumed,
                        'sold': sold
                    })
                    jmir_doc.flags.ignore_mandatory = True
                    jmir_doc.save(ignore_permissions=True)
                    idx = len(jmir_doc.textile_details_of_product) - 1
                    output = jmir_doc.textile_details_of_product[idx]
                    frappe.db.commit()
                    response('Data added sucessfully', output, 201)
                else :
                    response('Same data already added', {}, 400)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: add_details_of_product", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_details_of_product(jmi_id, row_id, p_type, p_desc, fiber_content, fun_jute, visiblity, test_report, produced, self_consumed, sold, attachment=None, approve=None, reject=None):
    '''
    Method to update Details of Products
    args:
        jmi_id : Registration Number of JMI Reg form
        row_id : Name of Child Table
        p_type : Product type
        p_desc : Product Description
        fiber_content : Fiber Content
        fun_jute : Function of jute material in the product
        visiblity : Whether Jute is Visible or Not Visible in the Product
        test_report : Test Report
        attachment : Attachment
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):

            self_consumed = int(self_consumed or 0)

            if not frappe.db.exists('Details of Products', row_id):
                return response('Data not found for this IDs!', {}, 400)
            elif not frappe.db.exists('Product Type', p_type):
                return response('Invalid Product Type selected', {}, 400)
            elif fun_jute and not frappe.db.exists('JMI Product Function', fun_jute):
                return response('Invalid Function of jute material in the product selected', {}, 400)
            elif visiblity not in ['Yes', 'No']:
                return response('Visibility should be either \'Yes\' or \'No\'', {}, 400)
            elif test_report not in ['Available', 'Not Available']:
                return response('Test Report should be either \'Available\' or \'Not Available\'', {}, 400)
            elif not (is_float(fiber_content) and is_jmi_percentage(fiber_content)):
                return response('Fiber Content should be in Percentage >= 50%!', {}, 400)
            elif not is_number(self_consumed):
                return response('Self Consumed should be a number greater than Zero!', {}, 400)
            elif int(produced or 0) < (int(sold or 0) + int(self_consumed or 0)):
                return response('Produced Qty should be greater than or equal to Sold+Self Consumed!', {}, 400)
            else:
                details_of_prod = frappe.get_doc('Details of Products', row_id)
                details_of_prod.update({
                    'product_type': p_type,
                    'product_description': p_desc,
                    'fiber_content': fiber_content,
                    'function_of_jute_material_in_the_product': fun_jute,
                    'whether_jute_is_visible_or_not_visible_in_the_product': visiblity,
                    'test_report_details': test_report,
                    'attachment': attachment,
                    'self_consumed': self_consumed,
                    'sold': sold,
                    'produced': produced
                })
                details_of_prod.flags.ignore_mandatory = True
                details_of_prod.save(ignore_permissions=True)

                jmir_doc = frappe.get_doc("Jute Mark India Registration form", jmi_id)
                for row in jmir_doc.textile_details_of_product:
                    if row.product_type ==  p_type and row.name == row_id:
                        if int(approve or 0):
                            row.approve = 1
                            row.reject = 0
                        elif int(reject or 0):
                            row.reject = 1
                            row.approve = 0
                jmir_doc.save(ignore_permissions=True)
                frappe.db.commit()
                output = get_values_from_child_table('Details of Products', jmi_id, row_id)
                return response('Data updated successfully', output, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_details_of_product", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def delete_details_of_product(jmi_id, row_id):
    '''
        Method to Delete Details of Products
        args:
            jmi_id : Registration Number of JMI Reg form
            p_type : Product type
            fun_jute : Function of jute material in the product
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            if frappe.db.exists('Details of Products', row_id):
                frappe.db.delete('Details of Products', row_id)
                frappe.db.commit()
                return response('Data deleted sucessfully', {}, 200)
            return response('Data not found with this IDs!', {}, 400)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_details_of_product", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_details_of_product(jmi_id):
    '''
        Method to get Details of Products
        args:
            jmi_id : Registration Number of JMI Reg form
    '''
    try :
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
                jmir_doc = frappe.get_doc("Jute Mark India Registration form", jmi_id)
                if jmir_doc.textile_details_of_product:
                    output = get_values_from_child_table('Details of Products', jmi_id)
                    response('Data get sucessfully', output, 200)
                else:
                    response('Data not available!', {}, 400)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_details_of_product", message=frappe.get_traceback())
        return response(exception, {}, 400)


@frappe.whitelist()
def update_approval_or_reject_status(jmi_id, name_of_unit__outlet=None, approve=None, reject=None):
    try:
        if frappe.db.exists("Jute Mark India Registration form", jmi_id):
            jmi_doc = frappe.get_doc("Jute Mark India Registration form", jmi_id)
            approve_reject_flg = None
            for row in jmi_doc.textile_details_of_production_units_or_retailer_sales_outlets:
                if (name_of_unit__outlet and row.name_of_unit__outlet == name_of_unit__outlet) \
                    or not name_of_unit__outlet:
                    if int(approve or 0):
                        row.approve = 1
                        row.reject = 0
                        approve_reject_flg = 'Approved'
                    elif int(reject or 0):
                        row.reject = 1
                        row.approve = 0
                        approve_reject_flg = 'Rejected'
            if not approve_reject_flg:
                return response('No row found for the Approve/Reject status update', {}, 404)
            jmi_doc.save(ignore_permissions=True)
            frappe.db.commit()
            return response('{0} successfully'.format(approve_reject_flg), {}, 200)
        else:
            response('JMI registration \'{0}\' not found!'.format(jmi_id), {}, 404)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_approval_or_reject_status", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def users_with_specific_role(role):
    '''
        Method to get users with given role
        args:
            role : Name of the Role
    '''
    try:
        if frappe.db.exists('Role', role):
            query = '''
                SELECT
                    u.name as email_id,
                    u.full_name as full_name
                FROM
                    `tabUser` u,
                    `tabHas Role` hr
                WHERE
                    u.name = hr.parent AND
                    hr.role = "{role}"
            '''.format(role=role)
            user_list = frappe.db.sql(query, as_dict=1)
            if len(user_list)>0:
                response('Data get sucessfully', user_list, 200)
            else:
                response('No Users found with this Role', [], 400)
        else:
            response('Role '+ role +' does not exist', {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: users_with_specific_role", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_jmi_registration_forms(assigned_to=None, status=None):
    '''
        Method to get JMI Registration forms
        args:
            assigned_to : User name to filter by assigned
            status : Workflow State
    '''
    try:
        sql_fields = "name as application_id, registration_number, date as application_date, applicant_name, workflow_state as status"
        query = '''
            SELECT
                {fields}
            FROM
                `tabJute Mark India Registration form`
            WHERE
                workflow_state in ('Assigned VO', 'Save','Submitted')
        '''.format(fields=sql_fields)
        if assigned_to:
            query += 'AND `tabJute Mark India Registration form`.`_assign` like "%{user}%"'.format(user=assigned_to)
            if status:
                query += 'AND workflow_state = "{status}"'.format(status=status)
        else:
            if status:
                query += 'AND workflow_state = "{status}"'.format(status=status)
        query += 'ORDER BY modified DESC'
        doc_list = frappe.db.sql(query, as_dict = 1)
        if len(doc_list)>0:
            response('Data get successfully', doc_list, 200)
        else:
            response('Data not found', [], 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_jmi_registration_forms", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_site_visit(site_visit_id, distance_in_km, schedule_date):
    '''
        Method to update site visit
        args:
            site_visit_id : Actual Site Visit Plan Id
            distance_in_km : Distance in KM
            schedule_date : Schedule Date
    '''
    try:
        if frappe.db.exists("Actual Site Visit Plan", site_visit_id):
            if frappe.db.get_value("Actual Site Visit Plan", site_visit_id, 'assigned_for'):
                assigned_for = frappe.db.get_value("Actual Site Visit Plan", site_visit_id, 'assigned_for')
                if assigned_for != frappe.session.user:
                    return response('Only Assigned VO will be able to Submit the Schedule!', { 'logged_in_user':frappe.session.user, 'assigned_user':assigned_for }, 400)
            if not distance_in_km:
                return response('Distance is Required!', {}, 400)
            elif not is_float(distance_in_km):
                return response('Distance is Invalid!', {}, 400)
            elif float(distance_in_km)<=0:
                return response('Distance in KM should be greater than Zero!', {}, 400)
            current_date = getdate(today())
            if getdate(schedule_date) < current_date:
                return response('Schedule Date should be furure date!', {}, 400)
            if frappe.db.get_value('Actual Site Visit Plan', site_visit_id, 'docstatus'):
                return response('Site Visit is already Submitted. You will be only able to Reschedule it!', {}, 400)
            else:
                site_visit_doc = frappe.get_doc('Actual Site Visit Plan', site_visit_id)
                site_visit_doc.distance_in_km = float(distance_in_km)
                site_visit_doc.visit_planed_on = getdate(schedule_date)
                site_visit_doc.save(ignore_permissions=True)
                site_visit_doc.submit()
                frappe.db.commit()
                response('Visit Scheduled Successfuly', { 'site_visit_id':site_visit_doc.name, 'distance_in_km':float(distance_in_km), 'scheduled_date':schedule_date, 'status':site_visit_doc.workflow_state }, 201)
        else:
            response('Actual Site Visit Plan \'{0}\' not found!'.format(site_visit_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_site_visit", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def reschedule_site_visit(site_visit_id, schedule_date):
    '''
        Method to Re-schedule site visit
        args:
            site_visit_id : Actual Site Visit Plan Id
            schedule_date : Schedule Date
    '''
    try:
        if frappe.db.exists("Actual Site Visit Plan", site_visit_id):
            if frappe.db.get_value("Actual Site Visit Plan", site_visit_id, 'assigned_for'):
                assigned_for = frappe.db.get_value("Actual Site Visit Plan", site_visit_id, 'assigned_for')
                if assigned_for != frappe.session.user:
                    return response('Only Assigned VO will be able to Reschedule Site Visit!', { 'logged_in_user':frappe.session.user, 'assigned_user':assigned_for }, 400)
            current_date = getdate(today())
            if getdate(schedule_date) < current_date:
                response('Schedule Date should be furure date!', {}, 400)
            else:
                application_no = frappe.db.get_value('Actual Site Visit Plan', site_visit_id, 'application_no')
                visit_planed_on = frappe.db.get_value('Actual Site Visit Plan', site_visit_id, 'visit_planed_on')
                frappe.db.set_value('Actual Site Visit Plan', site_visit_id, 'visit_planed_on', getdate(schedule_date))
                frappe.db.set_value('Actual Site Visit Plan',site_visit_id,'workflow_state','Pending')
                frappe.db.commit()
                response('Visit Rescheduled Successfuly', { 'application_no':application_no, 'site_visit_id':site_visit_id, 'scheduled_date':visit_planed_on, 'rescheduled_date':getdate(schedule_date) }, 201)
        else:
            response('Actual Site Visit Plan \'{0}\' not found!'.format(site_visit_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: reschedule_site_visit", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist()
def is_float(value):
    try:
        if float(value) >= 0:
            return True
        else:
            return False
    except ValueError:
        return False

@frappe.whitelist()
def is_number(value):
    try:
        if float(value) >= 0:
            return True
        else:
            return False
    except ValueError:
        return False

@frappe.whitelist()
def is_jmi_percentage(value):
    if (float(value)<50 or float(value)>100):
        return False
    else:
        return True

@frappe.whitelist(allow_guest=True)
def add_site_visit_photos(application_no, actual_site_visit_plan, unit_address, photograph_1, photograph_2, geo_location, latitude, longitude, no_of_male_artisan, no_of_female_artisan, no_of_other_artisan):
    '''
        Method to Add Site Visit Photos
        args:
            application_no : JMI Registration ID
            actual_site_visit_plan : Actual Site Visit Plan Id
            unit_address : Unit Address
            photograph_1 : File URL of Photograph 1
            photograph_2 : File URL of Photograph 2
            geo_location: Geo Location
            latitude : Latitude
            longitude : Longitude
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            if not frappe.db.exists('Actual Site Visit Plan', actual_site_visit_plan):
                return response('Actual Site Visit Plan \'{0}\' not found!'.format(actual_site_visit_plan), {}, 400)
            if getdate(frappe.db.get_value('Actual Site Visit Plan', actual_site_visit_plan, "visit_planed_on")) < getdate(today()):
                return response('Please enter future date in Actual Site Visit Plan!', {}, 400)
            if not frappe.db.exists('Textile_Details of Production Units or Retailer Sales Outlets', {'parent': application_no}):
                return response('Data not found for Details of Production Units/Retailer Sales Outlets!', {}, 400)
            if not is_number(no_of_male_artisan):
                return response('No of Male Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_female_artisan):
                return response('No of Female Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_other_artisan):
                return response('No of Other Artisan should be a number greater than Zero!', {}, 400)
            on_site_verification = get_on_site_verification_form(application_no)
            if on_site_verification:
                on_site_verification_doc = frappe.get_doc('On-Site Verification Form', on_site_verification)
                output = {
                    'actual_site_visit_plan' : actual_site_visit_plan,
                    'unit_address' : unit_address,
                    'photograph_1' : photograph_1,
                    'photograph_2' : photograph_2,
                    'geo_location' : geo_location,
                    'latitude' : latitude,
                    'longitude' : longitude,
                    'no_of_male_artisan':no_of_male_artisan,
                    'no_of_female_artisan':no_of_female_artisan,
                    'no_of_other_artisan':no_of_other_artisan
                }
                flag = 0
                for site_visit in on_site_verification_doc.site_visit_photos:
                    if site_visit.actual_site_visit_plan == actual_site_visit_plan:
                        if not site_visit.photograph_1 and not site_visit.photograph_2:
                            site_visit.photograph_1 = photograph_1
                            site_visit.photograph_2 = photograph_2
                            site_visit.geo_location = geo_location
                            site_visit.latitude = latitude
                            site_visit.longitude = longitude
                            flag = 1
                            break
                        else:
                            return response('Site Photos already added for this site', {}, 400)
                if flag == 1:
                    on_site_verification_doc.flags.ignore_mandatory = True
                    on_site_verification_doc.save(ignore_permissions=True)
                    output["site_visit_done"] = 1
                    visit_plan_doc = frappe.get_doc("Actual Site Visit Plan", actual_site_visit_plan)
                    visit_plan_doc.update({
                        'site_visit_done': 1,
                        'no_of_male_artisan': no_of_male_artisan,
                        'no_of_female_artisan': no_of_female_artisan,
                        'no_of_other_artisan': no_of_other_artisan
                    })
                    visit_plan_doc.flags.ignore_mandatory = True
                    visit_plan_doc.save(ignore_permissions=True)

                    ret_sales_outlet_nm = frappe.db.get_value('Textile_Details of Production Units or Retailer Sales Outlets',
                        {
                            'address': visit_plan_doc.address_visited,
                            'parent': application_no
                        },
                    "name")
                    if ret_sales_outlet_nm:
                        ret_sales_outlet = frappe.get_doc('Textile_Details of Production Units or Retailer Sales Outlets', ret_sales_outlet_nm)
                        ret_sales_outlet.update({
                            'no_of_male_artisan': no_of_male_artisan,
                            'no_of_female_artisan': no_of_female_artisan,
                            'no_of_other_artisan': no_of_other_artisan
                        })
                        ret_sales_outlet.flags.ignore_mandatory = True
                        ret_sales_outlet.save(ignore_permissions=True)
                    frappe.db.commit()
                    response('Site Visit Photos added sucessfully', output, 201)
            else :
                response('On Site Verification form not yet created!', {}, 400)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: add_site_visit_photos", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_site_visit_photos(application_no, actual_site_visit_plan, unit_address, photograph_1, photograph_2, geo_location, latitude, longitude):
    '''
        Method to Add Site Visit Photos
        args:
            application_no : JMI Registration ID
            actual_site_visit_plan : Actual Site Visit Plan Id
            unit_address : Unit Address
            photograph_1 : File URL of Photograph 1
            photograph_2 : File URL of Photograph 2
            geo_location: Geo Location
            latitude : Latitude
            longitude : Longitude
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            if not frappe.db.exists('Actual Site Visit Plan', actual_site_visit_plan):
                return response('Actual Site Visit Plan \'{0}\' not found!'.format(actual_site_visit_plan), {}, 400)
            on_site_verification = get_on_site_verification_form(application_no)
            if on_site_verification:
                on_site_verification_doc = frappe.get_doc('On-Site Verification Form', on_site_verification)
                output = {
                    'actual_site_visit_plan' : actual_site_visit_plan,
                    'unit_address' : unit_address,
                    'photograph_1' : photograph_1,
                    'photograph_2' : photograph_2,
                    'geo_location' : geo_location,
                    'latitude' : latitude,
                    'longitude' : longitude
                }
                for site_visit in on_site_verification_doc.site_visit_photos:
                    if site_visit.actual_site_visit_plan == actual_site_visit_plan:
                        frappe.db.set_value(site_visit.doctype, site_visit.name, 'unit_address', unit_address)
                        frappe.db.set_value(site_visit.doctype, site_visit.name, 'photograph_1', photograph_1)
                        frappe.db.set_value(site_visit.doctype, site_visit.name, 'photograph_2', photograph_2)
                        frappe.db.set_value(site_visit.doctype, site_visit.name, 'geo_location', geo_location)
                        frappe.db.set_value(site_visit.doctype, site_visit.name, 'latitude', latitude)
                        frappe.db.set_value(site_visit.doctype, site_visit.name, 'longitude', longitude)
                        frappe.db.commit()
                        return response('Site Visit Photos updated sucessfully', output, 200)
                response('Data not found for this site', {}, 400)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_site_visit_photos", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def delete_site_visit_photos(application_no, actual_site_visit_plan):
    '''
        Method to Add Site Visit Photos
        args:
            application_no : JMI Registration ID
            actual_site_visit_plan : Actual Site Visit Plan Id
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            on_site_verification = get_on_site_verification_form(application_no)
            if on_site_verification:
                on_site_verification_doc = frappe.get_doc('On-Site Verification Form', on_site_verification)
                for site_visit in on_site_verification_doc.site_visit_photos:
                    if site_visit.actual_site_visit_plan == actual_site_visit_plan:
                        frappe.db.set_value('Actual Site Visit Plan', actual_site_visit_plan, 'site_visit_done', 0)
                        site_visit.photograph_1 = None
                        site_visit.photograph_2 = None
                        site_visit.geo_location = None
                        site_visit.latitude =  None
                        site_visit.longitude = None
                        on_site_verification_doc.flags.ignore_mandatory = True
                        on_site_verification_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                        return response('Site Visit Photos deleted sucessfully', {}, 200)
                response('Data not found for this site', {}, 400)
            else:
                response('On Site Verification form not yet created!', {}, 400)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_site_visit_photos", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_site_visit_photos(application_no ,row_id = None):
    '''
        Method to Add Site Visit Photos
        args:
            application_no : JMI Registration ID
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            site_visit_doc = frappe.get_doc('Actual Site Visit Plan', {'application_no:',application_no})
            on_site_verification = get_on_site_verification_form(application_no)
            if on_site_verification:
                on_site_verification_doc = frappe.get_doc('On-Site Verification Form', on_site_verification)
                if on_site_verification_doc.site_visit_photos:
                    output = []
                    for site_visit in on_site_verification_doc.site_visit_photos:
                        output.append({
                            'application_no': application_no,
                            'actual_site_visit_plan': site_visit.actual_site_visit_plan,
                            'unit_address': site_visit.unit_address,
                            'photograph_1': site_visit.photograph_1,
                            'photograph_2': site_visit.photograph_2,
                            'geo_location': site_visit.geo_location,
                            'latitude': site_visit.latitude,
                            'longitude': site_visit.longitude,
                            "no_of_male_artisan": site_visit_doc.no_of_male_artisan,
                            "no_of_female_artisan": site_visit_doc.no_of_female_artisan,
                            "no_of_other_artisan": site_visit_doc.no_of_other_artisan
                        })
                    return response('Site Visit Photos get sucessfully', output, 200)
                else:
                    response('Data not found for this site', {}, 400)
            else:
                response('On Site Verification form not yet created!', {}, 400)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_site_visit_photos", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def add_documents(application_no, product_type, test_report, remarks):
    '''
        Method to Add Documents
        args:
            application_no : JMI Registration ID
            product_type : Product Type
            test_report : File Url of Test Report Attachment
            remarks : Remarks
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            if not test_report:
                return response('Test Report Attachment is required', {}, 400)
            if not frappe.db.exists('Product Type', product_type):
                return response('Product Type {} does not exists!'.format(product_type), {}, 400)
            jmir_doc = frappe.get_doc('Jute Mark India Registration form', application_no)
            flag = 0
            for document in jmir_doc.documents:
                if document.upload_test_report == test_report and document.product_type == product_type:
                    flag = 1
                    break
            if not flag:
                jmir_doc.append('documents', {
                    'upload_test_report' : test_report,
                    'product_type' : product_type,
                    'remarks' : remarks,
                })
                jmir_doc.flags.ignore_mandatory = True
                jmir_doc.save(ignore_permissions=True)
                frappe.db.commit()
                idx = len(jmir_doc.documents) - 1
                output = jmir_doc.documents[idx]
                response('Document added sucessfully', output, 201)
            else:
                response('Document already added!', {}, 400)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: add_documents", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def update_documents(application_no, row_id, product_type, test_report, remarks):
    '''
        Method to Add Documents
        args:
            application_no : JMI Registration ID
            row_id : Name of child table row
            product_type : Product Type
            test_report : File Url of Test Report Attachment
            remarks : Remarks
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            if not test_report:
                return response('Test Report Attachment is required', {}, 400)
            if not frappe.db.exists('Product Type', product_type):
                return response('Product Type {} does not exists!'.format(product_type), {}, 400)
            if frappe.db.exists('JMI Documents', row_id):
                reg_doc = frappe.get_doc("Jute Mark India Registration form", application_no)
                flag=0
                for row in reg_doc.documents:
                    if row.name == row_id and row.product_type == product_type:
                        flag = 1
                        break
                if flag == 1:
                    frappe.db.set_value('JMI Documents', row_id, 'upload_test_report', test_report)
                    #frappe.db.set_value('JMI Documents', row_id, 'product_type', product_type)
                    frappe.db.set_value('JMI Documents', row_id, 'remarks', remarks)
                    frappe.db.commit()
                    output = frappe.get_doc('JMI Documents', row_id)
                    response('Document updated sucessfully', output, 200)
                else:
                    response('Product Type is different for row id!', {}, 400)
            else:
                response('Document not found!', {}, 400)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_documents", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def delete_documents(application_no, row_id):
    '''
        Method to delete Documents
        args:
            application_no : JMI Registration ID
            row_id : name of child table row
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            if not frappe.db.exists('JMI Documents', row_id):
                return response('Document not found', {}, 400)
            frappe.db.delete('JMI Documents', row_id)
            frappe.db.commit()
            return response('Document deleted sucessfully', {}, 200)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_documents", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_documents(application_no):
    '''
        Method to Get Documents
        args:
            application_no : JMI Registration ID
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            jmir_doc = frappe.get_doc('Jute Mark India Registration form', application_no)
            if jmir_doc.documents:
                output = get_values_from_child_table('JMI Documents', application_no)
                return response('Document get sucessfully', output, 200)
            else:
                response('Document not found', {}, 400)
        else:
            response('Jute Mark India Registration form \'{0}\' not found!'.format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_documents", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist()
def delete_end_user(email_id):
    '''
        Method to Delete end user and it's log
        args:
            email_id: Email of end user
    '''
    try:
        if not email_id:
            return response('Email is required!', {}, 400)
        else:
            deleted_flag = False
            if frappe.db.exists('User', email_id):
                frappe.db.delete('User', email_id)
                deleted_flag = True
            if frappe.db.exists('Contact', { 'user':email_id }):
                frappe.db.delete('Contact', { 'user':email_id })
                deleted_flag = True
            if frappe.db.exists('User Registration', { 'email_id':email_id }):
                frappe.db.delete('User Registration', { 'email_id':email_id })
                deleted_flag = True
            if frappe.db.exists('Access Log', { 'user':email_id }):
                frappe.db.delete('Access Log', { 'user':email_id })
                deleted_flag = True
            if frappe.db.exists('Activity Log', { 'user':email_id }):
                frappe.db.delete('Activity Log', { 'user':email_id })
            if frappe.db.exists('Route History', { 'user':email_id }):
                frappe.db.delete('Route History', { 'user':email_id })
                deleted_flag = True
            if frappe.db.exists('ToDo', { 'allocated_to':email_id }):
                frappe.db.delete('ToDo', { 'allocated_to':email_id })
                deleted_flag = True
            if frappe.db.exists('Request for Label', { 'requested_by':email_id }):
                frappe.db.delete('Request for Label', { 'requested_by':email_id })
                deleted_flag = True
            if frappe.db.exists('Roll wise QR', { 'allocated_to_user':email_id }):
                frappe.db.delete('Roll wise QR', { 'allocated_to_user':email_id })
                deleted_flag = True
            if frappe.db.exists('Label Allocation', { 'requested_by':email_id }):
                frappe.db.delete('Label Allocation', { 'requested_by':email_id })
                deleted_flag = True
            if frappe.db.exists('User Device', { 'user':email_id }):
                frappe.db.delete('User Device', { 'user':email_id })
                deleted_flag = True
            if frappe.db.exists('Roll wise QR', { 'allocated_to_user':email_id }):
                frappe.db.delete('Roll wise QR', { 'allocated_to_user':email_id })
                deleted_flag = True
            if frappe.db.exists('JMI QR Code', { 'allocated_to_user':email_id }):
                frappe.db.delete('JMI QR Code', { 'allocated_to_user':email_id })
                deleted_flag = True
            if frappe.db.exists('Jute Mark India Registration form', { 'email_id':email_id }):
                jmi_id = frappe.db.get_value('Jute Mark India Registration form', { 'email_id':email_id })
                frappe.db.delete('Jute Mark India Registration form', jmi_id)
                if frappe.db.exists('Actual Site Visit Plan', { 'application_no': jmi_id }):
                    frappe.db.delete('Actual Site Visit Plan', { 'application_no': jmi_id })
                if frappe.db.exists('ToDo', { 'reference_name': jmi_id }):
                    frappe.db.delete('ToDo', { 'reference_name': jmi_id })
                if frappe.db.exists('On-Site Verification Form', { 'textile_registration_no': jmi_id }):
                    frappe.db.delete('On-Site Verification Form', { 'textile_registration_no': jmi_id })
                if frappe.db.exists('JMI Appeal', { 'application_no': jmi_id }):
                    frappe.db.delete('JMI Appeal', { 'application_no': jmi_id })
                if frappe.db.exists('Label Enhancement', { 'application_no': jmi_id }):
                    frappe.db.delete('Label Enhancement', { 'application_no': jmi_id })
                deleted_flag = True
            if deleted_flag:
                delete_user_password(email_id)
                frappe.db.commit()
                return response('User \'{0}\' Deleted Succesfully'.format(email_id), {}, 200)
            else:
                return response('No records found for User \'{0}\''.format(email_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_end_user", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist()
def validate_pan_number(pan_number):
    validated = False
    regex = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
    if(re.fullmatch(regex, pan_number)):
        validated = True
    return validated

@frappe.whitelist()
def validate_gst_number(gst_number):
    validated = False
    regex = '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if(re.fullmatch(regex, gst_number)):
        validated = True
    return validated

@frappe.whitelist()
def validate_aadhar_number(aadhar_number):
    validated = False
    if (len(str(aadhar_number)) == 12) and str(aadhar_number).isdigit() :
        validated = True
    regex = ("^[2-9]{1}[0-9]{3}\\" + "s[0-9]{4}\\s[0-9]{4}$")
    p = re.compile(regex)
    if(re.search(p, aadhar_number)):
        validated = True
    return validated

@frappe.whitelist()
def validate_udyog_aadhar(udyog_aadhar):
    validated = False
    if (len(str(udyog_aadhar)) == 20):
        validated = True
    regex = ("^[A-Z]{3}-[A-Z]{2}-[0-9]{2}-[0-9]{7}$")
    p = re.compile(regex)
    if(re.search(p,udyog_aadhar)):
        validated = True
    return validated


@frappe.whitelist(allow_guest=True)
def get_site_visit_details(application_no, assigned_to=None, doctype="Jute Mark India Registration form", docname=None):
    if doctype == "Jute Mark India Registration form":
        docname = application_no
        site_field = "textile_details_of_production_units_or_retailer_sales_outlets"
    else:
        site_field = "assign_vo_for_sites"
    site_visit_details = []
    is_primary_vo = False
    if frappe.db.exists('Jute Mark India Registration form', application_no):
        doc = frappe.get_doc(doctype, docname)
        for site_visit in doc.get(site_field):
            data = {
                "name": site_visit.name,
                "site_visit_id": site_visit.site_visit_id,
                "scheduled_date": None,
                "status": None,
                "photograph_1": None,
                "photograph_2": None,
                "geo_location": None,
                "latitude": None,
                "longitude": None,
                "name_of_unit__outlet": site_visit.get("name_of_unit__outlet"),
                "approve": site_visit.approve,
                "reject": site_visit.reject
            }
            insert_flag = False
            if (assigned_to and site_visit.assign_to == assigned_to) or (is_primary_vo and\
                (not site_visit.assign_to or (site_visit.assign_to).strip() == '')):
                insert_flag = True
            elif not assigned_to:
                insert_flag = True
            if insert_flag:
                if site_visit.site_visit_id:
                    site_visit_doc = frappe.get_doc('Actual Site Visit Plan', site_visit.site_visit_id)
                    if site_visit_doc.assigned_for == frappe.session.user and site_visit.idx == 1:
                        is_primary_vo = True
                    on_site_verification = get_on_site_verification_form(application_no)
                    if on_site_verification:
                        on_site_verification_doc = frappe.get_doc('On-Site Verification Form', on_site_verification)
                        if on_site_verification_doc.site_visit_photos:
                            for site_visit_photo in on_site_verification_doc.site_visit_photos:
                                if site_visit_photo.actual_site_visit_plan == site_visit_doc.name:
                                    data.update({
                                        "photograph_1": site_visit_photo.get("photograph_1"),
                                        "photograph_2": site_visit_photo.get("photograph_2"),
                                        "geo_location": site_visit_photo.get("geo_location"),
                                        "latitude": site_visit_photo.get("latitude"),
                                        "longitude": site_visit_photo.get("longitude")
                                    })
                    data.update({
                        "site_name": site_visit_doc.address_line1,
                        "address": site_visit_doc.address_visited,
                        "distance_in_km": site_visit_doc.distance_in_km,
                        "no_of_male_artisan": site_visit_doc.no_of_male_artisan,
                        "no_of_female_artisan": site_visit_doc.no_of_female_artisan,
                        "no_of_other_artisan": site_visit_doc.no_of_other_artisan,
                        "scheduled_date": site_visit_doc.visit_planed_on,
                        "assigned_for": site_visit_doc.assigned_for,
                        "status": site_visit_doc.workflow_state,
                        "is_primary_site": site_visit_doc.is_primary_site
                    })
                else:
                    if site_visit.assign_to == frappe.session.user and site_visit.idx == 1:
                        is_primary_vo = True
                    data.update({
                        "site_name": site_visit.name_of_unit__outlet,
                        "address": site_visit.address,
                        "distance_in_km": 0,
                        "no_of_male_artisan": site_visit.no_of_male_artisan,
                        "no_of_female_artisan": site_visit.no_of_female_artisan,
                        "no_of_other_artisan": site_visit.no_of_other_artisan,
                        "assigned_for": site_visit.assign_to,
                        "is_primary_site": 1 if site_visit.idx == 1 else 0
                    })
                site_visit_details.append(data)
        if is_primary_vo:
            [
                row.update({"assigned_for": frappe.session.user}) if not row.get("assigned_for") \
                else '' for row in site_visit_details
            ]
    return site_visit_details

@frappe.whitelist(allow_guest=True)
def get_site_lists(assigned_for=None, status=None, site_visit_id=None):
    '''
        Method to get Site Details with respect to user
        args:
            assigned_for: VO User Id
            status : Status of Site Visit
            site_visit_id : Actual Site Visit Plan docname
    '''
    try:
        if not assigned_for:
            assigned_for = frappe.session.user
        if not frappe.db.exists('User', assigned_for):
            return response('User \'{0}\' not found!'.format(assigned_for), {}, 400)
        user_roles = frappe.get_roles(assigned_for)
        if 'Verification Officer(VO)' in user_roles:
            query = f"""
                select asvp.name from `tabJute Mark India Registration form` jmi
                left join `tabActual Site Visit Plan` asvp on jmi.name = asvp.application_no
                where jmi.workflow_state not in ('Approved By RO', 'Approved By HO') and asvp.name is not null
                and asvp.assigned_for = '{assigned_for}'
            """
            if status:
                query += f" and asvp.workflow_state = '{status}'"
            if site_visit_id:
                query += f" and asvp.name = '{site_visit_id}'"
            actual_site_visits = frappe.db.sql(query, as_dict=True)
            site_visit_details = []
            for actual_site_visit in actual_site_visits:
                photo_1 = None
                photo_2 = None
                geo_location = None
                latitude = None
                longitude = None
                site_visit_doc = frappe.get_doc('Actual Site Visit Plan', actual_site_visit.name)
                on_site_verification = get_on_site_verification_form(site_visit_doc.application_no)

                approve = reject = 0
                approval_flg = frappe.db.get_value("Textile_Details of Production Units or Retailer Sales Outlets",
                        {"site_visit_id": actual_site_visit.name, "parent": site_visit_doc.application_no}, ["approve", "reject"])
                if approval_flg and len(approval_flg) == 2:
                    approve, reject = approval_flg

                if on_site_verification:
                    on_site_verification_doc = frappe.get_doc('On-Site Verification Form', on_site_verification)
                    if on_site_verification_doc.site_visit_photos:
                        for site_visit in on_site_verification_doc.site_visit_photos:
                            if site_visit.actual_site_visit_plan == site_visit_doc.name:
                                photo_1 = site_visit.photograph_1
                                photo_2 = site_visit.photograph_2
                                geo_location = site_visit.geo_location
                                latitude = site_visit.latitude
                                longitude = site_visit.longitude
                site_visit_details.append({
                    "application_id" : site_visit_doc.application_no,
                    "site_visit_id": actual_site_visit.name,
                    "site_name": site_visit_doc.address_line1,
                    "address": site_visit_doc.address_visited,
                    "distance_in_km": site_visit_doc.distance_in_km,
                    "no_of_male_artisan": site_visit_doc.no_of_male_artisan,
                    "no_of_female_artisan": site_visit_doc.no_of_female_artisan,
                    "no_of_other_artisan": site_visit_doc.no_of_other_artisan,
                    "scheduled_date": site_visit_doc.visit_planed_on,
                    "assigned_for": site_visit_doc.assigned_for,
                    "status": site_visit_doc.workflow_state,
                    "is_primary_site": site_visit_doc.is_primary_site,
                    "photograph_1" : photo_1,
                    "photograph_2" : photo_2,
                    "geo_location" : geo_location,
                    "latitude" : latitude,
                    "longitude" : longitude,
                    "approve": approve,
                    "reject": reject
                })
            if site_visit_details:
                sorted_site_visit_details = sorted(site_visit_details, key=lambda k: k.get("scheduled_date"), reverse=True)
                return response('Sucesfully get data', sorted_site_visit_details, 200)
            else:
                if not frappe.db.exists('Actual Site Visit Plan', {'assigned_for': assigned_for}):
                    return response('Sites are not yet assigned to you!', {}, 400)
                else:
                    return response('Data not found!', {}, 400)
        else:
            return response("\'{0}\' is not a Verification Officer!".format(assigned_for), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_site_lists", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist()
def add_signature(application_no, signature_file_url):
    '''
        Method add Signature to On Site Verification form
        args:
            application_no : JMI Registration Number
            signature_file_url : File Url of Signature
    '''
    try:
        if frappe.db.exists("Jute Mark India Registration form", application_no):
            on_site_verification = get_on_site_verification_form(application_no)
            if on_site_verification:
                if frappe.db.exists('File', { 'file_url':signature_file_url }):
                    frappe.db.set_value('On-Site Verification Form', on_site_verification, 'signature_with_name', signature_file_url)
                    frappe.db.commit()
                    return response('Signature added Succesfully', { 'application_no':application_no, 'signature_file_url':signature_file_url }, 201)
                else:
                    return response('No file found with this file url. Please upload file!', {}, 400)
            else:
                return response('On Site Verification form not yet created!', {}, 400)
        else:
            return response("Jute Mark India Registration form \'{0}\' not found!".format(application_no), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: add_signature", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_jmi_uom(product_type, uom=None):
    '''Method to get JMI UOM List '''
    try:
        if frappe.db.exists('Product Type', product_type):
            query = '''
                SELECT
                    jmi_uom
                FROM
                    `tabProduct Type UOM`
                WHERE
                    parent = "{product_type}"
            '''.format(product_type=product_type)
            if uom:
                query += 'AND jmi_uom like "%{jmi_uom}%"'.format(jmi_uom=uom)
            uom_list = frappe.db.sql(query, as_dict = 1)
            if len(uom_list)>0:
                response('Data get sucessfully', uom_list, 200)
            else:
                response('Data not found', [], 400)
        else:
            response('Product Type {0} does not exist'.format(product_type), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_jmi_uom", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def jmi_product_functions(jmi_product_function=None):
    '''Method to get JMI Product Function List '''
    try:
        if jmi_product_function:
            jmi_product_function_list = frappe.get_all('JMI Product Function', fields = ['jmi_product_function'], filters={'jmi_product_function': ['like', '%' + jmi_product_function + '%' ]})
        else:
            jmi_product_function_list = frappe.get_all('JMI Product Function', fields = ['jmi_product_function'])
        if len(jmi_product_function_list)>0:
            response('Data get sucessfully', jmi_product_function_list, 200)
        else:
            response('Data not found', [], 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: jmi_product_functions", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_product_type(product_type=None):
    '''Method to get Product Type List '''
    try:
        if product_type:
            product_type_list = frappe.get_all('Product Type', fields = ['product_type'], filters={'product_type': ['like', '%' + product_type + '%' ]})
        else:
            product_type_list = frappe.get_all('Product Type', fields = ['product_type'])
        if len(product_type_list)>0:
            response('Data get sucessfully', product_type_list, 200)
        else:
            response('Data not found', [], 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_product_type", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def remove_attachment_from_doc(reference_doctype, reference_docname, reference_field):
    '''
        API for Attach existing file to any document
        args:
            reference_doctype : Doctype Name
            reference_docname : Document Name
            reference_field : name of field which attachment is atttached
    '''
    try:
        if not frappe.db.exists('DocType', reference_doctype):
            return response('Invalid Reference DocType', {}, 400)
        if not frappe.db.exists(reference_doctype, reference_docname):
            return response('Invalid Reference Docname', {}, 400)
        if not frappe.db.exists('DocField', { 'parent':reference_doctype, 'fieldname':reference_field, 'fieldtype': ['in', ['Attach', 'Attach Image']] }):
            return response('Invalid Reference Field', {}, 400)
        frappe.db.set_value(reference_doctype, reference_docname, reference_field, '')
        frappe.db.commit()
        return response('File removed sucessfully', {}, 200)
    except Exception as exception:
        frappe.log_error(title="Mobile API: remove_attachment_from_doc", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_identification_proofs():
    '''
        Method to get Identification Proofs
    '''
    try:
        identification_proof_list = []
        identification_proofs = ['Aadhaar Card', 'Driving License', 'Election Commission ID Card', 'Other government issued ID card', 'Passport']
        for identification_proof in identification_proofs:
            identification_proof_list.append({'identification_proof':identification_proof })
        response('Data get sucessfully', identification_proof_list, 200)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_identification_proofs", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_values_from_child_table(child_table, parent, name=None):
    query = '''
        SELECT
            *
        FROM
            `tab{0}`
        WHERE
            parent = '{1}'
    '''.format(child_table, parent)
    if name:
        query += " AND name = '"+ name +"'"
    data = frappe.db.sql(query, as_dict = 1)
    return data

@frappe.whitelist()
def delete_user_password(user_id):
    query = '''
        DELETE FROM
            `__Auth`
        WHERE
            doctype = 'User' AND
            name = '{0}'
    '''.format(user_id)
    data = frappe.db.sql(query, as_dict = 1)
    return data

@frappe.whitelist()
def delete_attachment(file_url):
    '''Method to delete file '''
    try:
        if frappe.db.exists('File', { 'file_url':file_url }):
            frappe.db.delete('File', { 'file_url':file_url })
            frappe.db.commit()
            return response('File deleted successfully', {}, 200)
        else:
            response('File does not exists with this url!', [], 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_attachment", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_JuteMarkIndiaRegistrationform_list(data=None):
    data=json.loads(frappe.request.data)
    try:
        jute_mark_india = frappe.db.sql("""SELECT name, applicant_name From `tabJute Mark India Registration form` where (owner='{0}' or email_id='{0}') and workflow_state in ('Approved By RO', 'Approved By HO') """.format(data.get("user_id")), as_dict=1)
        for row in jute_mark_india:
            row["on_site_verification"] = frappe.db.get_value("On-Site Verification Form", {"textile_registration_no": row.get("name")}, "name")
            row["no_of_labels"] = frappe.db.get_value("On-Site Verification Form", {"textile_registration_no": row.get("name")}, "no_of_labels")

            label_balance = 0.0
            labels = 0.0
            used_labels = 0.0
            application_doc = frappe.get_doc("Jute Mark India Registration form",{'name':row.get("name")})
            no_of_labels = frappe.db.get_value("On-Site Verification Form", {'textile_registration_no':row.get("name")}, 'no_of_labels')
            app_date = application_doc.date
            todays_date = date.today()
            cur_year = todays_date.year
            if app_date.year == cur_year:
                labels_per_month = int(no_of_labels/12)
                if app_date.day>=25:
                    months = 12-app_date.month
                else:
                    months = 12-app_date.month+1
                labels = months*labels_per_month
                if labels%10 != 0:
                    labels += 10-(labels%10)
            else:
                labels = no_of_labels
            data = frappe.db.sql("""select sum(required_qty) as total from `tabRequest for Label` where requested_by = '{0}' and docstatus=1 and EXTRACT(YEAR FROM posting_date) = '{1}' """.format(data.get("user"),cur_year),as_dict=1)
            if not data[0].total:
                used_labels = 0
            else:
                used_labels = data[0].total
            label_balance = labels - used_labels
            row["labels_balance"] = label_balance
        return {"status_code":200, "success":True, "error":"", "data":jute_mark_india}
    except Exception as e:
        frappe.log_error(title="Mobile API: get_JuteMarkIndiaRegistrationform_list", message=frappe.get_traceback())
        return {"status":401, "success":False, "error":e}


@frappe.whitelist()
def create_label_enhancement(data=None):
    '''
    params:
    application_no
    no_of_labels
    required_no_of_labels
    label_type
    reason_for_enhancement
    user_id
    labels_balance
    total_label_as_per_prorata
    '''
    data = json.loads(data)
    application_doc = frappe.get_doc("Jute Mark India Registration form",data.get("application_no"))
    if not(application_doc.workflow_state == "Approved By HO" or application_doc.workflow_state == "Approved By RO"):
        return {"status_code":401, "success":False, "error":"applcation not in approved state!"}
    elif data.get("no_of_labels") == 0:
        return {"status_code":401, "success":False, "error":"Please contact your Regional Officer, Since no labels allocated for this application!"}
    elif data.get("required_no_of_labels") < data.get("no_of_labels"):
        return {"status_code":401, "success":False, "error":"Required no. of Labels is less than current label count!"}
    else:
        try:
            doc = frappe.new_doc("Label Enhancement")
            doc.workflow_state = "Draft"
            doc.application_no = data.get("application_no")
            doc.label_type = data.get("label_type")
            doc.required_no_of_labels = data.get("required_no_of_labels")
            doc.reason_for_enhancement = data.get("reason_for_enhancement")
            doc.user_id = data.get("user_id")
            doc.labels_balance = data.get("labels_balance")
            doc.total_label_as_per_prorata = data.get("total_label_as_per_prorata")
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("Label Enhancement", doc.name, "workflow_state", "Pending")
            frappe.db.set_value("Jute Mark India Registration form",doc.application_no,"application_label_enhancement",1)
            frappe.db.commit()
            return {"status_code":200, "success":True, "error":"", "data":doc}
        except Exception as e:
            frappe.log_error(title="Mobile API: create_label_enhancement", message=frappe.get_traceback())
            return {"status_code":401, "success":False, "error":e}

@frappe.whitelist(allow_guest=True)
def get_requested_label_enhancement(on_site_verification):
    if frappe.db.exists("On-Site Verification Form",on_site_verification):
        on_site_verification_doc = frappe.get_doc("On-Site Verification Form",on_site_verification)
        if on_site_verification_doc.label_enhancement:
            return {"status_code":200, "success":True, "error":"", "requested_labels":on_site_verification_doc.no_of_label_requested}
        else:
            return {"status_code":401, "success":False, "error":"Label Enhancement not Requested yet!"}
    else:
        return {"status_code":401, "success":False, "error":"On-Site Verification Form with this id is not present!"}

@frappe.whitelist(allow_guest=True)
def get_approved_label_enhancement(on_site_verification):
    if frappe.db.exists("On-Site Verification Form", on_site_verification):
        on_site_verification_doc = frappe.get_doc("On-Site Verification Form", on_site_verification)
        if on_site_verification_doc.label_enhancement:
            if on_site_verification_doc.no_of_label_approved == 0:
                return {"status_code":401, "success":False, "error":"Label Enhancement Request is not Approved yet!"}
            else:
                return {"status_code":200, "success":True, "error":"", "approved_labels":on_site_verification_doc.no_of_label_approved}
        else:
            return {"status_code":401, "success":False, "error":"Label Enhancement not Requested yet!"}
    else:
        return {"status_code":401, "success":False, "error":"On-Site Verification Form with this id is not present!"}


@frappe.whitelist(allow_guest=True)
def update_label_enhancement(data=None):
    data = json.loads(data)
    if data.get("required_no_of_labels") < data.get("no_of_labels"):
        return {"status_code":401, "success":False, "error":"Required no. of Labels is less than current label count!"}
    if data.get("no_of_label_approved") < data.get("no_of_labels"):
        return {"status_code":401, "success":False, "error":"No. of Label Approved must be greater than equal to No Of Labels."}
    try:
        frappe.db.set_value("On-Site Verification Form", data.get("on_site_verification"), "no_of_labels", data.get("no_of_labels"))
        frappe.db.set_value("On-Site Verification Form", data.get("on_site_verification"), "no_of_label_approved", data.get("no_of_label_approved"))
        frappe.db.commit()
        return {"status_code":200, "success":True, "error":"", "data":data}
    except Exception as e:
        frappe.log_error(title="Mobile API: update_label_enhancement", message=frappe.get_traceback())
        return {"status_code":401, "success":False, "error":e}

@frappe.whitelist(allow_guest=True)
def update_JMIAppeal(data=None):
    data = json.loads(frappe.request.data)
    try:
        if not frappe.db.exists("On-Site Verification Form", data.get("on_site_verification")):
            return response('Invalid On-Site Verification Form', {}, 401)
        frappe.db.set_value("On-Site Verification Form", data.get("on_site_verification"), "no_of_labels", data.get("no_of_labels"))
        frappe.db.set_value("On-Site Verification Form", data.get("on_site_verification"), "workflow_state", "Approval Pending By RO")
        frappe.db.commit()
        return {"status_code":200, "success":True, "error":"", "data":data}
    except Exception as e:
        frappe.log_error(title="Mobile API: update_JMIAppeal", message=frappe.get_traceback())
        return {"status_code":401, "success":False, "error":e}

@frappe.whitelist(allow_guest=True)
def create_ApplicationRenewal(data=None):
    data = json.loads(frappe.request.data)
    try:
        if not frappe.db.exists("Jute Mark India Registration form", data.get("application_no")):
            return response('Invalid Registration number', {}, 401)
        application_date, renewal_flag = frappe.db.get_value("Jute Mark India Registration form",
            data.get("application_no"), ["date", "application_renewal"])
        if not renewal_flag:
            return response('You cannot do Renewal, Your Application Valid till today!', {}, 401)
        doc = frappe.new_doc("Application Renewal")
        doc.workflow_state = "Draft"
        doc.appealing_date = today()
        doc.application_date = application_date
        doc.application_no = data.get("application_no")
        doc.applicant_name = data.get("applicant_name")
        doc.on_site_verification = data.get("on_site_verification")
        doc.reason_for_enhancement = data.get("reason_for_enhancement")
        doc.user_id = data.get("user_id")
        doc.save(ignore_permissions=True)
        jmir_doc = frappe.get_doc("Jute Mark India Registration form", doc.application_no)
        for row in jmir_doc.textile_details_of_production_units_or_retailer_sales_outlets:
            if row.approve == 1:
                row.approve = 0
            if row.reject == 1:
                row.reject = 0
        for row in jmir_doc.textile_details_of_product:
            if row.approve == 1:
                row.approve = 0
            if row.reject == 1:
                row.reject = 0
        jmir_doc.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.db.set_value("Application Renewal", doc.name, "workflow_state", "Pending")
        frappe.db.commit()
        doc.workflow_state = "Pending"
        return response('Application Renewal created sucessfully', doc, 201)
    except Exception as e:
        frappe.log_error(title="Mobile API: create_ApplicationRenewal", message=frappe.get_traceback())
        return {"status_code":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def update_ApplicationRenewal(data=None):
    data = json.loads(frappe.request.data)
    try:
        if not frappe.db.exists("On-Site Verification Form", data.get("on_site_verification")):
            return response('Invalid On-Site Verification Form ID', {}, 401)
        frappe.db.set_value("On-Site Verification Form", \
            data.get("on_site_verification"), "workflow_state", "Approval Pending By RO")
        frappe.db.commit()
        return {"status_code":200, "success":True, "error":"", "data":data}
    except Exception as e:
        frappe.log_error(title="Mobile API: update_ApplicationRenewal", message=frappe.get_traceback())
        return {"status_code":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def get_lable_enhancement_list(user):
    roles = frappe.get_roles(user)
    if 'JMI User' in roles:
        try:
            label_enhancement = frappe.db.sql("""
                SELECT name, application_no, applicant_name, total_label_as_per_prorata, workflow_state,
                on_site_verification, label_type, reason_for_enhancement, no_of_labels, required_no_of_labels
                From `tabLabel Enhancement` where user_id = '{0}'
            """.format(user), as_dict=True)
            return {"status_code":200, "success":True, "error":"", "data":label_enhancement}
        except Exception as e:
            frappe.log_error(title="Mobile API: get_lable_enhancement_list", message=frappe.get_traceback())
            return {"status":401, "success":False, "error":e}
    elif 'Verification Officer(VO)' in roles:
        try:
            label_enhancement = frappe.db.sql("""select distinct le.name, le.application_no, le.applicant_name, le.total_label_as_per_prorata, le.workflow_state, le.on_site_verification, le.label_type, le.reason_for_enhancement, le.no_of_labels, le.required_no_of_labels from `tabLabel Enhancement` le join `tabLabel Enhancement VO Assignment` a on le.name = a.parent  where a.assign_to = '{0}' """.format(user), as_dict=1)
            for row in label_enhancement:
                sites = []
                output = get_values_from_child_table('Label Enhancement VO Assignment',row.name)
                for row1 in output:
                    if row1.assign_to == user:
                        sites.append(row1)
                row['site_details'] = sites
            return {"status_code":200, "success":True, "error":"", "data":label_enhancement}
        except Exception as e:
            frappe.log_error(title="Mobile API: get_lable_enhancement_list", message=frappe.get_traceback())
            return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def get_JMIAppeal_list(data=None):
    data=json.loads(frappe.request.data)
    try:
        JMIAppeal = frappe.db.sql("""
            select name, application_no, applicant_name, appeal_type, application_remarks, appealing_date,
            jmi_appeal, application_date, no_of_labels, no_of_label_requested, previous_appealing_date
            from `tabJMI Appeal` where (user_id='{0}')
        """.format(data.get("user_id")), as_dict=True)
        return {"status_code":200, "success":True, "error":"", "data":JMIAppeal}
    except Exception as e:
        frappe.log_error(title="Mobile API: get_JMIAppeal_list", message=frappe.get_traceback())
        return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def get_ApplicationRenewal_list(data=None):
    data=json.loads(frappe.request.data)
    try:
        ApplicationRenewal = frappe.db.sql("""
            SELECT workflow_state, name, application_no, applicant_name, on_site_verification
            From `tabApplication Renewal` where (user_id='{0}')
        """.format(data.get("user_id")), as_dict=True)
        return {"status_code":200, "success":True, "error":"", "data":ApplicationRenewal}
    except Exception as e:
        frappe.log_error(title="Mobile API: get_ApplicationRenewal_list", message=frappe.get_traceback())
        return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def create_request_for_label(user, required_qty):
    if int(required_qty or 0) < 50 or not validate_label_count(int(required_qty or 0)):
        return response('The quantity must be a multiple of 10, and a minimum of 50 is necessary.',{}, 400)
    if user and frappe.db.exists("User",user):
        ro_office = ""
        #is_ro = 0
        user_doc = frappe.get_doc("User",user)
        roles = frappe.db.sql("""
            select role from `tabHas Role` where parent = '{0}' and parenttype='User'
        """.format(user),as_dict=True)
        if any(d['role'] == 'JMI User' for d in roles):
            if not frappe.db.exists("Jute Mark India Registration form",{'email_id':user}):
                return response('Regional Office not present as Registration Id not generated yet for JMI User',{}, 400)
            else:
                ro_office = frappe.db.get_value("Jute Mark India Registration form",{'email_id':user},'regional_office')
            balance_qty = get_balance_label(user)

            if balance_qty:
                if  int(required_qty or 0) > int(balance_qty or 0):
                    return response('balance quantity for user \'{0}\' is \'{1}\'' .format(user,balance_qty),{}, 400)
                else:
                    try:
                        doc = frappe.new_doc("Request for Label")
                        doc.requested_by = user
                        doc.regional_office = ro_office
                        doc.required_qty = int(required_qty or 0)
                        doc.is_ro = 0
                        jmi_registration_form, category_b = frappe.db.get_value("Jute Mark India Registration form", {
                            "email_id": user
                        }, ["name", "category_b"], order_by="modified desc") or ("", "")
                        fees_filter = { "category": category_b, "fees_description": "Label Request"}
                        fees_amt = frappe.db.get_value("Fees Records", fees_filter, "amount") or 0
                        doc.jmi_registration_form = jmi_registration_form or ""
                        doc.save(ignore_permissions=True)
                        data = doc.as_dict()
                        data["amount"] = flt(fees_amt) * int(doc.required_qty)
                        frappe.db.commit()
                        return response('Request for Label added sucessfully', data, 201)
                    except Exception as e:
                        frappe.log_error(title="Mobile API: create_request_for_label", message=frappe.get_traceback())
                        return response("Unable to create Request for Label",{},400)
        else:
            return response('User \'{0}\' is not JMI User!'.format(user), {}, 400)
    else:
        return response('User \'{0}\' not found!'.format(user), {}, 400)

@frappe.whitelist(allow_guest=True)
def submit_request_for_label(label_request_id):
    '''Submit Request for Lable if payment is completed'''
    try:
        if not frappe.db.exists('Request for Label', label_request_id):
            return {"status_code": 404, "success": False, "error": "Given Request for Label does't exist"}
        else:
            doc = frappe.get_doc("Request for Label", label_request_id)
            if not doc.is_paid:
                return {"status_code": 403, "success": False, "error": "Payment is pending for Request for Label"}
            elif doc.docstatus == 1:
                return {"status_code": 403, "success": False, "error": "Request for Label is already Submitted"}
            else:
                doc.flags.ignore_validate = True
                doc.submit()
                return {"status_code": 200, "success": True, "error": ""}
    except Exception as e:
        frappe.log_error(title="Mobile API: submit_request_for_label", message=frappe.get_traceback())
        return {"status_code":401, "success":False, "error":e}

@frappe.whitelist(allow_guest=True)
def get_balance_label(user):
    application_doc = frappe.get_doc("Jute Mark India Registration form",{'email_id':user})
    if application_doc.workflow_state == 'Approved By RO' or application_doc.workflow_state =='Approved By HO':
        if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':application_doc.name}):
            no_of_labels = frappe.db.get_value("On-Site Verification Form",{'textile_registration_no':application_doc.name},['no_of_labels'])
            app_date = application_doc.date
            todays_date = date.today()
            cur_year = todays_date.year
            if app_date.year == cur_year:
                labels_per_month = int(no_of_labels/12)
                if app_date.day>=25:
                    months = 12-app_date.month
                else:
                    months = 12-app_date.month+1
                labels = months*labels_per_month
                if labels%10 != 0:
                    labels += 10-(labels%10)
            else:
                labels = no_of_labels
            data = frappe.db.sql("""select sum(required_qty) as total from `tabRequest for Label` where requested_by = '{0}' and docstatus=1 and EXTRACT(YEAR FROM posting_date) = '{1}' """.format(user,cur_year),as_dict=1)
            if not data[0].total:
                used_labels = 0
            else:
                used_labels = data[0].total
            unused_labels= labels - used_labels
            return int(unused_labels or 0)
        else:
            return response('On-Site Verification form is not created yet for user \'{0}\'' .format(user),{}, 400)
    else:
        return response('Jute Mark India Registration form with id : \'{0}\' is not Approved ' .format(application_doc.name),{}, 400)

@frappe.whitelist(allow_guest=True)
def get_label_status(user):
    try:
        application_doc = frappe.get_doc("Jute Mark India Registration form",{'email_id': user})
        if application_doc.workflow_state == 'Approved By RO' or application_doc.workflow_state =='Approved By HO':
            if frappe.db.exists("On-Site Verification Form",{'textile_registration_no':application_doc.name}):
                no_of_labels = frappe.db.get_value("On-Site Verification Form",{'textile_registration_no':application_doc.name},['no_of_labels'])
                app_date = application_doc.date
                todays_date = date.today()
                cur_year = todays_date.year
                if app_date.year == cur_year:
                    labels_per_month = int(no_of_labels/12)
                    if app_date.day>=25:
                        months = 12-app_date.month
                    else:
                        months = 12-app_date.month+1
                    total_labels = months*labels_per_month
                    if total_labels%10 != 0:
                        total_labels += 10-(total_labels%10)
                else:
                    total_labels = no_of_labels
                #return int(labels)
                data = frappe.db.sql("""
                    select sum(required_qty) as total from `tabRequest for Label`
                    where requested_by = '{0}' and docstatus=1 and EXTRACT(YEAR FROM posting_date) = '{1}'
                """.format(user, cur_year),as_dict=True)
                if not data[0].total:
                    used_labels = 0
                else:
                    used_labels = data[0].total
                unused_labels= total_labels - used_labels
                data = {
                "total_labels" : int(total_labels or 0),
                "balance_labels" : int(unused_labels or 0),
                "used_labels" : int(used_labels or 0)
                }
                return {"status_code":200, "success":True, "error":"", "data":data}
            else:
                message = "On-Site Verification form is not created yet for user \'{0}\'".format(data.get("user"))
                return {"status":401, "success":False, "error":"" ,"message":message}
        else:
            message = 'Jute Mark India Registration form with id : \'{0}\' is not Approved '.format(application_doc.name),
            return {"status":401, "success":False, "error":"" ,"message":message}
    except Exception as e:
        frappe.log_error(title="Mobile API: get_label_status", message=frappe.get_traceback())
        return {"status":401, "success":False, "error":e}

@frappe.whitelist(allow_guest=True)
def get_label_request_list(user):
    try:
        label_request = frappe.db.sql("""
            select name,posting_date,required_qty, requested_by, regional_office, remarks
            from `tabRequest for Label` where requested_by='{}' and docstatus=1
            """.format(user), as_dict=True)
        return {"status_code":200, "success":True, "error":"", "data":label_request}
    except Exception as e:
        frappe.log_error(title="Mobile API: get_label_request_list", message=frappe.get_traceback())
        return {"status":401, "success":False, "error":e}


@frappe.whitelist(allow_guest=True)
def get_label_type():
    data=[
        {"label_type": "Temporary"},
        {"label_type": "Permanent"}
    ]
    return {"status_code":200, "success":True, "error":"", "data":data}


@frappe.whitelist(allow_guest=True)
def get_appeal_type(data=None):
    data=json.loads(frappe.request.data)
    workflow_state = frappe.db.get_value("Jute Mark India Registration form", data.get("application_no"), "workflow_state")
    appeal = frappe.db.get_value("JMI Appeal", {
        "application_no":data.get("application_no")
    }, "name")
    appeal_type = []
    if appeal:
        appeal_type.append({"appeal_type": "Appeal for Escalation"})
    elif workflow_state in ["Approved By RO", "Approved By HO"]:
        appeal_type.append({"appeal_type": "Appeal for Approval"})
    elif workflow_state in ["Rejected by RO", "Rejected by HO"]:
        appeal_type.append({"appeal_type": "Appeal for Rejection"})
    return {"status_code":200, "success":True, "error":"", "data":appeal_type}


@frappe.whitelist(allow_guest=True)
def get_application_no(user):
    '''
        Method to get on application id  from user
       user: User
    '''
    roles = frappe.db.sql("""select role from `tabHas Role` where parent = '{0}' and parenttype='User'""".format(user),as_dict=True)
    if any(d['role'] == 'JMI User' for d in roles):
        if frappe.db.exists('Jute Mark India Registration form',{
            'email_id': user,'workflow_state': ['in', ['Approved By HO', 'Approved By RO']]
            }):
            application_no = frappe.get_doc('Jute Mark India Registration form',{'email_id':user,'workflow_state':['in',['Approved By HO', 'Approved By RO']]}).name
            return application_no
        else:
            return {"status_code":404, "success":False, "error":"Your Registration Form is not in approved state"}


@frappe.whitelist(allow_guest=True)
def get_site_visit_details_enhancement(application_no, label_enhance_doc):
    return get_site_visit_details(application_no, assigned_to=None, doctype="Label Enhancement", docname=label_enhance_doc)


@frappe.whitelist(allow_guest=True)
def update_label_enhancement_site_details(label_enhance_id, row_id, address, no_of_male_artisan, no_of_female_artisan, no_of_other_artisan):
    '''
        Method to update child doc - Assign VO for Sites on LAbel Enhancement
        args:
            label_enhance_id : Label Enhancement Document id
            row_id : Name of Child Table
            address : Address
            no_of_male_artisan : No of Male Artisan
            no_of_female_artisan : No of Female Artisan
            no_of_other_artisan : No of Other Artisan
    '''

    try :
        if frappe.db.exists("Label Enhancement",label_enhance_id):
            label_enhance_doc = frappe.get_doc("Label Enhancement",label_enhance_id)
            if label_enhance_doc.workflow_state == "Assigned VO":
                if not frappe.db.exists('Label Enhancement VO Assignment', row_id):
                    return response('Data not found with this IDs!', {}, 400)
                if not is_number(no_of_male_artisan):
                    return response('No of Male Artisan should be a number greater than Zero!', {}, 400)
                if not is_number(no_of_female_artisan):
                    return response('No of Female Artisan should be a number greater than Zero!', {}, 400)
                if not is_number(no_of_other_artisan):
                    return response('No of Other Artisan should be a number greater than Zero!', {}, 400)
                frappe.db.set_value('Label Enhancement VO Assignment', row_id, 'address', address)
                frappe.db.set_value('Label Enhancement VO Assignment', row_id, 'no_of_male_artisan', no_of_male_artisan)
                frappe.db.set_value('Label Enhancement VO Assignment', row_id, 'no_of_female_artisan', no_of_female_artisan)
                frappe.db.set_value('Label Enhancement VO Assignment', row_id, 'no_of_other_artisan', no_of_other_artisan)
                frappe.db.commit()

                output = get_values_from_child_table('Label Enhancement VO Assignment', label_enhance_id, row_id)

                #updating value inside Actual site visit plan
                label_enh_doc = frappe.get_doc("Label Enhancement",label_enhance_id)
                for row in label_enh_doc.assign_vo_for_sites:
                    if row.name == row_id and row.assign_to:
                        actual_site_visit = frappe.db.get_value("Actual Site Visit Plan", {"name": row.site_visit_id, "assigned_for": row.assign_to})
                        if actual_site_visit:
                            frappe.db.set_value('Actual Site Visit Plan', actual_site_visit, 'no_of_male_artisan', no_of_male_artisan)
                            frappe.db.set_value('Actual Site Visit Plan', actual_site_visit, 'no_of_female_artisan', no_of_female_artisan)
                            frappe.db.set_value('Actual Site Visit Plan', actual_site_visit, 'no_of_other_artisan', no_of_other_artisan)
                            frappe.db.commit()
                return response('Data updated successfully', output, 200)
            else:
                response('Label Enhancement \'{0}\' not in Assigned VO state!'.format(label_enhance_id),{},400)
        else:
            response('Label Enhancement \'{0}\' not found!'.format(label_enhance_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: update_label_enhancement_site_details", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def delete_label_enhancement_site_details(label_enhance_id, row_id):
    '''
        Method to Delete child doc row - Assign VO for Sites on LAbel Enhancement
        args:
            jmi_id : Registration Number of JMI Reg form
            row_id : Name of Child Table row
    '''
    try :
        if frappe.db.exists("Label Enhancement",label_enhance_id):
            label_enhance_doc = frappe.get_doc("Label Enhancement",label_enhance_id)
            if label_enhance_doc.workflow_state == "Assigned VO":
                if not frappe.db.exists('Label Enhancement VO Assignment', row_id):
                    return response('Data not found for this IDs!', {}, 400)
                frappe.db.delete('Label Enhancement VO Assignment', row_id)
                frappe.db.commit()
                return response('Lable Enhancement related site is deleted', {}, 200)
            else:
                response('Label Enhancement \'{0}\' not in Assigned VO state!'.format(label_enhance_id),{},400)
        else:
            response('Label Enhancement\'{0}\' not found!'.format(label_enhance_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: delete_label_enhancement_site_details", message=frappe.get_traceback())
        return response(exception, {}, 400)

@frappe.whitelist(allow_guest=True)
def get_site_details_label_enhancement(label_enhance_id):
    '''
        Method to get Assign Vo For Sites
        args:
            label_enhanc_id: Label Enhancemnet id
    '''
    try:
        if frappe.db.exists("Label Enhancement",label_enhance_id):
            doc = frappe.get_doc("Label Enhancement",label_enhance_id)
            output = get_values_from_child_table('Label Enhancement VO Assignment',label_enhance_id)
            if len(output):
                response('Data Get sucessfully', output, 200)
            else:
                response('Data not found!', {}, 400)
        else:
            response('Label Enhancement \'{0}\' not found!'.format(label_enhance_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: get_site_details_label_enhancement", message=frappe.get_traceback())
        return response(exception, {}, 400)


@frappe.whitelist(allow_guest=True)
def add_sites_label_enhancement(label_enhance_id, name_of_unit, address, no_of_male_artisan, no_of_female_artisan, no_of_other_artisan, application_no = None):
    '''
        Method to add
        args:
            label_enhanc_id: Label Enhancemnet id
            name_of_unit : Name of Unit / Outlet
            address : Address
            no_of_male_artisan : No of Male Artisan
            no_of_female_artisan : No of Female Artisan
            no_of_other_artisan : No of Other Artisan
    '''
    try :
        if frappe.db.exists("Label Enhancement",label_enhance_id):

            if not is_number(no_of_male_artisan):
                return response('No of Male Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_female_artisan):
                return response('No of Female Artisan should be a number greater than Zero!', {}, 400)
            if not is_number(no_of_other_artisan):
                return response('No of Other Artisan should be a number greater than Zero!', {}, 400)
            label_enhance_doc = frappe.get_doc("Label Enhancement",label_enhance_id)
            if label_enhance_doc.workflow_state == "Assigned VO":
                category = frappe.get_doc("Jute Mark India Registration form",label_enhance_doc.application_no).category_b
                if category != 'Artisan':
                    values = label_enhance_doc.assign_vo_for_sites
                    flag = 0
                    for row in values:
                        if row.name_of_unit__outlet==name_of_unit and row.address==address:
                            flag = 1
                            break
                    if flag == 0:
                        label_enhance_doc.append('assign_vo_for_sites',{
                            'name_of_unit__outlet':name_of_unit,
                            'address' : address,
                            'no_of_male_artisan' : no_of_male_artisan,
                            'no_of_female_artisan' : no_of_female_artisan,
                            'no_of_other_artisan' : no_of_other_artisan
                        })
                        label_enhance_doc.flags.ignore_mandatory = True
                        label_enhance_doc.save(ignore_permissions=True)
                        jmir_doc = frappe.get_doc("Jute Mark India Registration form", label_enhance_doc.application_no)
                        for row in jmir_doc.textile_details_of_production_units_or_retailer_sales_outlets:
                            if row.approve == 1:
                                row.approve = 0
                            if row.reject == 1:
                                row.reject = 0
                        for row in jmir_doc.textile_details_of_product:
                            if row.approve == 1:
                                row.approve = 0
                            if row.reject == 1:
                                row.reject = 0
                        jmir_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                        idx = len(label_enhance_doc.assign_vo_for_sites) - 1
                        output = label_enhance_doc.assign_vo_for_sites[idx]
                        response('Data added sucessfully', output, 201)
                    else :
                        response('Same data already added!', {}, 400)
                else:
                    response('Production Units can not be added for Artisan!', {}, 400)
            else:
                response('Label Enhancement \'{0}\' not in Assigned VO state!'.format(label_enhance_id),{},400)
        else:
            response('Label Enhancement \'{0}\' not found!'.format(label_enhance_id), {}, 400)
    except Exception as exception:
        frappe.log_error(title="Mobile API: add_sites_label_enhancement", message=frappe.get_traceback())
        return response(exception, {}, 400)



@frappe.whitelist(allow_guest=True)
def create_JMIAppeal(data=None):
    data = json.loads(frappe.request.data)
    try:
        if frappe.db.exists('JMI Appeal', {
            'application_no': data.get("application_no"),
            'appeal_type': data.get("appeal_type")
        }):
            return {"status_code": 401, "success": False, "error": "Appeal is Already created against this appplication!!"}
        else:
            doc = frappe.new_doc("JMI Appeal")
            doc.workflow_state = "Draft"
            doc.appealing_date = today()
            doc.application_date = frappe.db.get_value("Jute Mark India Registration form", data.get("application_no"), "date")
            doc.application_no = data.get("application_no")
            doc.applicant_name = data.get("applicant_name")
            doc.appeal_type = data.get("appeal_type")
            doc.on_site_verification = data.get("on_site_verification")
            doc.no_of_labels = data.get("no_of_labels")
            doc.no_of_label_requested = data.get("no_of_label_requested")
            doc.application_remarks = data.get("application_remarks")
            doc.user_id = data.get("user_id")
            doc.labels_balance = data.get("labels_balance")
            doc.save(ignore_permissions=True)
            frappe.db.commit()
            frappe.db.set_value("JMI Appeal", doc.name, "workflow_state", "Pending")
            frappe.db.commit()
            doc.workflow_state = "Pending"
            return {"status_code":200, "success":True, "error":"", "data":doc}
    except Exception as e:
        frappe.log_error(title="Mobile API: create_JMIAppeal", message=frappe.get_traceback())
        return {"status_code":401, "success":False, "error":e}
