from datetime import timedelta
import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_total_application():
	registered_application= frappe.db.sql(""" select state, count(name) as total_application from `tabJute Mark India Registration form` WHERE workflow_state in ("Approved By RO", "Approved By HO") Group By state;""",as_dict=1)

	state_wise_data = [ {"id":"IN.AP","value":0},
    	  {"id":"IN.AR","value":0},
          {"id":"IN.AS","value":0},
          {"id":"IN.BR","value":0},
          {"id":"IN.CH","value":0},
          {"id":"IN.CT","value":0},
          {"id":"IN.DN","value":0},
          {"id":"IN.DD","value":0},
          {"id":"IN.DL","value":0},
          {"id":"IN.GA","value":0},
          {"id":"IN.GJ","value":0},
          {"id":"IN.HR","value":0},
          {"id":"IN.HP","value":0},
          {"id":"IN.JH","value":0},
          {"id":"IN.KA","value":0},
          {"id":"IN.KL","value":0},
          {"id":"IN.LD","value":0},
          {"id":"IN.MP","value":0},
          {"id":"IN.MH","value":0},
          {"id":"IN.MNL","value":0},
          {"id":"IN.ML","value":0},
          {"id":"IN.MZ","value":0},
          {"id":"IN.NL","value":0},
          {"id":"IN.OR","value":0},
          {"id":"IN.PY","value":0},
          {"id":"IN.PB","value":0},
          {"id":"IN.RJ","value":0},
          {"id":"IN.SK","value":0},
          {"id":"IN.TN","value":0},
          {"id":"IN.TR","value":0},
          {"id":"IN.UP","value":0},
          {"id":"IN.UT","value":0},
          {"id":"IN.WB","value":0},
          {"id":"IN.TG","value":0},
          {"id":"IN.JK","value":0},
          {"id":"IN.LA","value":0},
          {"id":"IN.AN","value":0}];

	for row in registered_application:
		for s1 in state_wise_data:
			if row['state'] == 'MAHARASHTRA' and s1['id'] == 'IN.MH':
				s1['value'] = row['total_application']
			if row['state'] == 'ANDHRA PRADESH' and s1['id'] == 'IN.AP':
				s1['value'] = row['total_application']
			if row['state'] == 'LADAKH' and s1['id'] == 'IN.LA':
				s1['value'] = row['total_application']
			if row['state'] == 'ARUNACHAL PRADESH' and s1['id'] == 'IN.AR':
				s1['value'] = row['total_application']
			if row['state'] == 'ASSAM' and s1['id'] == 'IN.AS':
				s1['value'] = row['total_application']
			if row['state'] == 'BIHAR' and s1['id'] == 'IN.BR':
				s1['value'] = row['total_application']
			if row['state'] == 'CHANDIGARH' and s1['id'] == 'IN.CH':
				s1['value'] = row['total_application']
			if row['state'] == 'CHHATTISGARH' and s1['id'] == 'IN.CT':
				s1['value'] = row['total_application']
			if row['state'] == 'THE DADRA AND NAGAR HAVELI AND DAMAN AND DIU' and s1['id'] == 'IN.DD':
				s1['value'] = row['total_application']
			if row['state'] == 'DELHI' and s1['id'] == 'IN.DL':
				s1['value'] = row['total_application']
			if row['state'] == 'GOA' and s1['id'] == 'IN.GA':
				s1['value'] = row['total_application']
			if row['state'] == 'GUJARAT' and s1['id'] == 'IN.GJ':
				s1['value'] = row['total_application']
			if row['state'] == 'HARYANA' and s1['id'] == 'IN.HR':
				s1['value'] = row['total_application']
			if row['state'] == 'HIMACHAL PRADESH' and s1['id'] == 'IN.HP':
				s1['value'] = row['total_application']
			if row['state'] == 'JHARKHAND' and s1['id'] == 'IN.JH':
				s1['value'] = row['total_application']
			if row['state'] == 'KARNATAKA' and s1['id'] == 'IN.KA':
				s1['value'] = row['total_application']
			if row['state'] == 'KERALA' and s1['id'] == 'IN.KL':
				s1['value'] = row['total_application']
			if row['state'] == 'LAKSHADWEEP' and s1['id'] == 'IN.LD':
				s1['value'] = row['total_application']
			if row['state'] == 'MADHYA PRADESH' and s1['id'] == 'IN.MP':
				s1['value'] = row['total_application']
			if row['state'] == 'MANIPUR' and s1['id'] == 'IN.MNL':
				s1['value'] = row['total_application']
			if row['state'] == 'MEGHALAYA' and s1['id'] == 'IN.ML':
				s1['value'] = row['total_application']
			if row['state'] == 'MIZORAM' and s1['id'] == 'IN.MZ':
				s1['value'] = row['total_application']
			if row['state'] == 'NAGALAND' and s1['id'] == 'IN.NL':
				s1['value'] = row['total_application']
			if row['state'] == 'ODISHA' and s1['id'] == 'IN.OR':
				s1['value'] = row['total_application']
			if row['state'] == 'PUDUCHERRY' and s1['id'] == 'IN.PY':
				s1['value'] = row['total_application']
			if row['state'] == 'PUNJAB' and s1['id'] == 'IN.PB':
				s1['value'] = row['total_application']
			if row['state'] == 'RAJASTHAN' and s1['id'] == 'IN.RJ':
				s1['value'] = row['total_application']
			if row['state'] == 'SIKKIM' and s1['id'] == 'IN.SK':
				s1['value'] = row['total_application']
			if row['state'] == 'TAMIL NADU' and s1['id'] == 'IN.TN':
				s1['value'] = row['total_application']
			if row['state'] == 'TRIPURA' and s1['id'] == 'IN.TR':
				s1['value'] = row['total_application']
			if row['state'] == 'UTTAR PRADESH' and s1['id'] == 'IN.UP':
				s1['value'] = row['total_application']
			if row['state'] == 'UTTARAKHAND' and s1['id'] == 'IN.UT':
				s1['value'] = row['total_application']
			if row['state'] == 'WEST BENGAL' and s1['id'] == 'IN.WB':
				s1['value'] = row['total_application']
			if row['state'] == 'TELANGANA' and s1['id'] == 'IN.TG':
				s1['value'] = row['total_application']
			if row['state'] == 'JAMMU AND KASHMIR' and s1['id'] == 'IN.JK':
				s1['value'] = row['total_application']
			if row['state'] == 'Andaman and Nicobar' and s1['id'] == 'IN.AN':
				s1['value'] = row['total_application']
			# if row['state'] == '' and s1['id'] == 'IN.DN':
			# 	s1['value'] = row['total_application']

	return state_wise_data


@frappe.whitelist()
def get_state_details(state):
	regional_office_list =  frappe.db.sql("""select Distinct regional_office from `tabJute Mark India Registration form` where state='{0}';""".format(state))
	if regional_office_list:
		#Creating Regional Office wise Data
		reg_data = []
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			row = {}
			row['regional_office'] = regional_office			
			application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office}))
			row['application_received'] = application_received			
			verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Assigned VO'}))
			row['verification_pending'] = verification_pending
			registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approved By RO'}))
			row['registered_application'] = registered_application
			rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Rejected by RO'}))
			row['rejected_application'] = rejected_application
			approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approval Pending By RO'}))
			row['approval_pending'] = approval_pending
			reg_data.append(row)
		#creating Maufacture list 
		manufacturer_list = []
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			row = {}
			row['regional_office'] = regional_office
			application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'category_b':'Manufacturer'}))
			row['application_received'] = application_received	
			verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Assigned VO','category_b':'Manufacturer'}))
			row['verification_pending'] = verification_pending
			registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approved By RO','category_b':'Manufacturer'}))
			row['registered_application'] = registered_application
			rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Rejected by RO','category_b':'Manufacturer'}))
			row['rejected_application'] = rejected_application
			approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approval Pending By RO','category_b':'Manufacturer'}))
			row['approval_pending'] = approval_pending
			manufacturer_list.append(row)
		#creating Artisen list 
		artisan_list = []
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			row = {}
			row['regional_office'] = regional_office
			application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'category_b':'Artisan'}))
			row['application_received'] = application_received			
			verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Assigned VO','category_b':'Artisan'}))
			row['verification_pending'] = verification_pending
			registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approved By RO','category_b':'Artisan'}))
			row['registered_application'] = registered_application
			rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Rejected by RO','category_b':'Artisan'}))
			row['rejected_application'] = rejected_application
			approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approval Pending By RO','category_b':'Artisan'}))
			row['approval_pending'] = approval_pending
			artisan_list.append(row)
		#creating Artisen list 
		retailer_list = []
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			row = {}
			row['regional_office'] = regional_office
			application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'category_b':'Retailer'}))
			row['application_received'] = application_received			
			verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'','category_b':'Retailer'}))
			row['verification_pending'] = verification_pending
			registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approved By RO','category_b':'Retailer'}))
			row['registered_application'] = registered_application
			rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Rejected by RO','category_b':'Retailer'}))
			row['rejected_application'] = rejected_application
			approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approval Pending By RO','category_b':'Retailer'}))
			row['approval_pending'] = approval_pending
			retailer_list.append(row)
		#creating Atisen Cast wise data 
		artisan_cast_list = []
		cast_list = ['SC','ST','Other']
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			for cast in cast_list:
				row = {}
				row['regional_office'] = regional_office
				row['cast'] = cast
				application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'category_b':'Artisan','category__scst_other_in_case_b_is_1':cast}))
				row['application_received'] = application_received				
				verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Assigned VO','category_b':'Artisan','category__scst_other_in_case_b_is_1':cast}))
				row['verification_pending'] = verification_pending
				registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approved By RO','category_b':'Artisan','category__scst_other_in_case_b_is_1':cast}))
				row['registered_application'] = registered_application
				rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Rejected by RO','category_b':'Artisan','category__scst_other_in_case_b_is_1':cast}))
				row['rejected_application'] = rejected_application
				approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approval Pending By RO','category_b':'Artisan','category__scst_other_in_case_b_is_1':cast}))
				row['approval_pending'] = approval_pending
				if application_received > 0:
					artisan_cast_list.append(row)
		#creating Atisen gender wise data 
		artisan_gender_list = []
		gender_list = ['Male','Female','Other']
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			for gender in gender_list:
				row = {}
				row['regional_office'] = regional_office
				row['gender'] = gender
				application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'category_b':'Artisan','gender':gender}))
				row['application_received'] = application_received				
				verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Assigned VO','category_b':'Artisan','gender':gender}))
				row['verification_pending'] = verification_pending
				registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approved By RO','category_b':'Artisan','gender':gender}))
				row['registered_application'] = registered_application
				rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Rejected by RO','category_b':'Artisan','gender':gender}))
				row['rejected_application'] = rejected_application
				approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approval Pending By RO','category_b':'Artisan','gender':gender}))
				row['approval_pending'] = approval_pending
				if application_received > 0:
					artisan_gender_list.append(row)
		#creating Atisen Religion wise data 
		artisan_religion_list = []
		religion_list = ['Buddhism','Christian','Hindu','Islam','Jain','Others','Sikh']
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			for religion in religion_list:
				row = {}
				row['regional_office'] = regional_office
				row['religion'] = religion
				application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'category_b':'Artisan','religion':religion}))
				row['application_received'] = application_received				
				verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Assigned VO','category_b':'Artisan','religion':religion}))
				row['verification_pending'] = verification_pending
				registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approved By RO','category_b':'Artisan','religion':religion}))
				row['registered_application'] = registered_application
				rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Rejected by RO','category_b':'Artisan','religion':religion}))
				row['rejected_application'] = rejected_application
				approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'regional_office':regional_office,'workflow_state':'Approval Pending By RO','category_b':'Artisan','religion':religion}))
				row['approval_pending'] = approval_pending
				if application_received > 0:
					artisan_religion_list.append(row)
		#creating Atisen Label Status 
		artisan_labels = []
		for reg_office in regional_office_list:
			r1 = list(reg_office)
			regional_office = r1[0]
			row = {}
			row['regional_office'] = regional_office
			reg_officer = frappe.db.get_value("User wise RO",{'regional_office':regional_office},'name')
			available_labels = len(frappe.db.get_list("JMI QR Code",{'allocated_to':regional_office}))
			row['labels_in_stock'] = available_labels
			requested_labels = frappe.db.sql("""select sum(r.required_qty) from `tabRequest for Label` as r join `tabJute Mark India Registration form` as j on r.requested_by = j.email_id where r.regional_office='{0}' and r.docstatus=1 and r.requested_by!='{1}' and j.category_b="Artisan";""".format(regional_office,reg_officer))
			if requested_labels[0][0]:
				row['requsted_labels'] = int(requested_labels[0][0])
			else:
				row['requsted_labels'] = 0
			deliverd_labels = frappe.db.sql("""select sum(l.total_no_of_labels) from `tabLabel Allocation` as l join `tabJute Mark India Registration form` as j on l.requested_by = j.email_id where l.regional_office='{0}' and l.docstatus=1 and l.requested_by!='{1}' and j.category_b="Artisan";""".format(regional_office,reg_officer))
			if deliverd_labels[0][0]:	
				row['delivered_labels'] = int(deliverd_labels[0][0])
			else:
				row['delivered_labels'] = 0
			row['remaining_for_order'] = row['requsted_labels'] - row['delivered_labels']
			artisan_labels.append(row)

	else:
		frappe.throw(_("Data is not available for State : {0}".format(state)))

	return reg_data,artisan_list,manufacturer_list,retailer_list,artisan_cast_list,artisan_gender_list,artisan_religion_list,artisan_labels


@frappe.whitelist()
def get_state_wise_data():
	state_list = frappe.db.get_list("State",pluck='name')
	state_data = []
	app_receive = veri_pending = regi_apps = rejected_apps = appr_pending = 0
	for state in state_list:
		row = {}
		row['state'] = state
		application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state}))
		row['application_received'] = application_received		
		app_receive += application_received

		verification_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'workflow_state':'Assigned VO'}))
		row['verification_pending'] = verification_pending
		veri_pending += verification_pending

		registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'workflow_state':'Approved By RO'}))
		row['registered_application'] = registered_application
		regi_apps += registered_application

		rejected_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'workflow_state':'Rejected by RO'}))
		row['rejected_application'] = rejected_application
		rejected_apps += rejected_application

		approval_pending = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'workflow_state':'Approval Pending By RO'}))
		row['approval_pending'] = approval_pending
		appr_pending += approval_pending
		state_data.append(row)

	total_row = {
		"state": "Total",
		"application_received": app_receive,
		"verification_pending": veri_pending,
		"registered_application": regi_apps,
		"rejected_application": rejected_apps,
		"approval_pending": appr_pending
	}
	state_data.append(total_row)
	return state_data


@frappe.whitelist()
def get_overall_data(state=None):
	data = {}
	label_data = {}
	if state==None:
		application_received = len(frappe.db.get_list("Jute Mark India Registration form"))
		data['application_received'] = application_received
		registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'workflow_state': ['in',['Approved By RO','Approved By HO']]}))	
		data['registered_application'] = registered_application
		sc_application = len(frappe.db.get_list("Jute Mark India Registration form",{'category__scst_other_in_case_b_is_1':'SC'}))
		data['sc_application'] = sc_application
		st_application = len(frappe.db.get_list("Jute Mark India Registration form",{'category__scst_other_in_case_b_is_1':'ST'}))
		data['st_application'] = st_application
		other_cast_application = len(frappe.db.get_list("Jute Mark India Registration form",{'category__scst_other_in_case_b_is_1':'Other'}))
		data['other_cast_application'] = other_cast_application
		male_application = len(frappe.db.get_list("Jute Mark India Registration form",{'gender':'Male'}))
		data['male_application'] = male_application
		female_application = len(frappe.db.get_list("Jute Mark India Registration form",{'gender':'Female'}))
		data['female_application'] = female_application
		other_gender_application = len(frappe.db.get_list("Jute Mark India Registration form",{'gender':'Other'}))
		data['other_gender_application'] = other_gender_application
		
		sold_labels = len(frappe.db.get_list("JMI QR Code",{'status':'Allocated'}))
		label_data['sold_labels'] = sold_labels
		sc_labels = frappe.db.sql("""select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.category__scst_other_in_case_b_is_1 = 'SC'; """)
		label_data['sc_labels'] = int(sc_labels[0][0])
		st_labels = frappe.db.sql("""select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.category__scst_other_in_case_b_is_1 = 'ST'; """)
		label_data['st_labels'] = int(st_labels[0][0])
		other_cast_labels = frappe.db.sql("""select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.category__scst_other_in_case_b_is_1 = 'Other'; """)
		label_data['other_cast_labels'] = int(other_cast_labels[0][0])
		male_labels = frappe.db.sql(""" select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where gender="Male";""")
		label_data['male_labels'] = int(male_labels[0][0])
		female_labels = frappe.db.sql(""" select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where gender="Female";""")
		label_data['female_labels'] = int(female_labels[0][0])
		other_gender_labels = frappe.db.sql(""" select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where gender="Female";""")
		label_data['other_gender_labels'] = int(other_gender_labels[0][0])
	else:
		application_received = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state}))
		data['application_received'] = application_received
		registered_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'workflow_state': ['in',['Approved By RO','Approved By HO']]}))	
		data['registered_application'] = registered_application
		sc_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'category__scst_other_in_case_b_is_1':'SC'}))
		data['sc_application'] = sc_application
		st_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'category__scst_other_in_case_b_is_1':'ST'}))
		data['st_application'] = st_application
		other_cast_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'category__scst_other_in_case_b_is_1':'Other'}))
		data['other_cast_application'] = other_cast_application
		male_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'gender':'Male'}))
		data['male_application'] = male_application
		female_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'gender':'Female'}))
		data['female_application'] = female_application
		other_gender_application = len(frappe.db.get_list("Jute Mark India Registration form",{'state':state,'gender':'Other'}))
		data['other_gender_application'] = other_gender_application

		sold_labels = frappe.db.sql("""select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.state = '{0}'; """.format(state))
		label_data['sold_labels'] = int(sold_labels[0][0])
		sc_labels = frappe.db.sql("""select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.state = '{0}' and j.category__scst_other_in_case_b_is_1 = 'SC'; """.format(state))
		label_data['sc_labels'] = int(sc_labels[0][0])
		st_labels = frappe.db.sql("""select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.state = '{0}' and j.category__scst_other_in_case_b_is_1 = 'ST'; """.format(state))
		label_data['st_labels'] = int(st_labels[0][0])
		other_cast_labels = frappe.db.sql("""select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.state = '{0}' and  j.category__scst_other_in_case_b_is_1 = 'Other'; """.format(state))
		label_data['other_cast_labels'] = int(other_cast_labels[0][0])
		male_labels = frappe.db.sql(""" select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.state = '{0}' and gender="Male";""".format(state))
		label_data['male_labels'] = int(male_labels[0][0])
		female_labels = frappe.db.sql(""" select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.state = '{0}' and gender="Female";""".format(state))
		label_data['female_labels'] = int(female_labels[0][0])
		other_gender_labels = frappe.db.sql(""" select count(q.name) as total from `tabJMI QR Code` as q join `tabJute Mark India Registration form` as j on q.allocated_to_user = j.email_id where j.state = '{0}' and  gender="Female";""".format(state))
		label_data['other_gender_labels'] = int(other_gender_labels[0][0])

	return data,label_data

@frappe.whitelist(allow_guest=True)
def get_registration_info(reg_no):
	user_info = frappe.get_all("Jute Mark India Registration form",
		filters={
			"registration_number": reg_no,
			"workflow_state": ["in", ["Approved By RO", "Approved By HO"]]
		},
		fields=[
			"registration_number","entity_full_name", "applicant_name", "next_renewal_date","district","state"
		]
	)

	try:
		if user_info and isinstance(user_info[0], dict):
			if user_info[0]['next_renewal_date']:
				user_info[0]['next_renewal_date'] -= timedelta(days=1)
			return user_info[0]
		return {"registration_number":None,"entity_full_name":None, "next_renewal_date":None,"district":None,"state":None}
	except:
		return {"registration_number":None,"entity_full_name":None, "next_renewal_date":None,"district":None,"state":None}
	
@frappe.whitelist(allow_guest=True)
def fetch_states_data():
	application_received = frappe.get_all("Jute Mark India Registration form",
		fields=["state", "COUNT(name) AS total_count"],
		group_by="state"
	)
	registered_application = frappe.get_all("Jute Mark India Registration form",
		filters={"workflow_state": ["in", ["Approved By RO", "Approved By HO"]]},
		fields=["state", "COUNT(name) AS total_count"],
		group_by="state"
	)
	sold_indents = frappe.db.sql("""
		SELECT j.state, SUM(rq.required_qty) AS total
		FROM `tabRequest for Label` AS rq
		JOIN `tabJute Mark India Registration form` AS j
		ON rq.app__reg_number = j.registration_number WHERE rq.is_ro != 1
		GROUP BY j.state;
	""", as_dict=True)


	sold_labels = frappe.db.sql("""
		SELECT j.state, COUNT(q.name) AS total
		FROM `tabJMI QR Code` AS q
		JOIN `tabJute Mark India Registration form` AS j ON q.allocated_to_user = j.email_id
		GROUP BY j.state
	""", as_dict=True)

	states_data = []
	apps_received = regi_apps = sold_indent_sum = sold_labels_sum = 0
	for state in application_received:
		state_entry = {
			"state": state["state"],
			"application_received": state["total_count"],
			"registered_application": 0,
			"sold_indent": 0,
			"sold_labels": 0,
		}

		apps_received += state["total_count"]
		for reg_app in registered_application:
			if reg_app["state"] == state["state"]:
				state_entry["registered_application"] = reg_app["total_count"]
				regi_apps += reg_app["total_count"]

		for sold_indent in sold_indents:
			if sold_indent["state"] == state["state"]:
				state_entry["sold_indent"] = sold_indent["total"]
				sold_indent_sum += sold_indent["total"]

		for sold_label in sold_labels:
			if sold_label["state"] == state["state"]:
				state_entry["sold_labels"] = sold_label["total"]
				sold_labels_sum += sold_label["total"]

		states_data.append(state_entry)

	states_data.append({
		"state": "Total",
		"application_received": apps_received,
		"registered_application": regi_apps,
		"sold_indent": sold_indent_sum,
		"sold_labels": sold_labels_sum,
	})
	return states_data