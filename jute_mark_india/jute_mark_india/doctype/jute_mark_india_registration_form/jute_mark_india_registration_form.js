// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Jute Mark India Registration form', {
	onload_post_render: function(frm) {
		frm.get_field('save_next_1').$input.addClass('btn-primary');
		frm.get_field('save_next_2').$input.addClass('btn-primary');
		frm.get_field('save_next_3').$input.addClass('btn-primary');
		frm.get_field('save_submit').$input.addClass('btn-primary');
		if( frappe.session.user != 'Administrator' && frappe.user_roles.includes ('JMI User')){
			change_button_properties(frm);
			$('#jute-mark-india-registration-form-connections_tab-tab').hide();
			$('.form-dashboard-section').hide();
		}
		if( frappe.session.user != 'Administrator'){
			$('.form-attachments').hide();
			$('.form-assignments').hide();
			frm.scroll_to_field('category_b');
		}
	},
	refresh: function(frm) {
		frm.add_custom_button('Make Payment', function()
            {
				if(frm.doc.is_paid == 1){
					frappe.msgprint("Payment Already Proceeded !")
				}else{
				frappe.call({
					doc : frm.doc,
					method: 'get_amount',
				
					callback: function (r) {
						console.log(r)
						if(!r.exc){
							var url = "/payment-confirmation?amount="+r.message+"&doctype="+frm.doc.doctype+"&docname="+frm.doc.name
							console.log(url)
							window.open(url, "_self");
						}
					}
				});
			}
        });
		set_filters(frm);
		change_field_properties(frm);
		make_fields_mandatory(frm);
		if ((frm.doc.workflow_state == 'Approved By RO') || (frm.doc.workflow_state == 'Approved By HO')){
			cur_frm.set_df_property('registration_number', 'hidden', 0);
		}
		else {
			cur_frm.set_df_property('registration_number', 'hidden', 1);
		}
		if(frm.is_new()){
			cur_frm.set_df_property('details_of_product_tab','hidden',1);
			cur_frm.set_df_property('contact_details_tab','hidden',1);
		}
		else {
			cur_frm.set_df_property('details_of_product_tab','hidden',0);
			cur_frm.set_df_property('contact_details_tab','hidden',0);
		}
		if(frm.is_new() && !frm.doc.email_id){
			frm.set_value('email_id', frappe.session.user);
		}
		if(cur_frm.doc.attach_sample_report){
			cur_frm.set_df_property('sample_report','hidden',1)
		}
		else{
			cur_frm.set_df_property('sample_report','hidden',0)
		}
		if(frappe.user_roles.includes ('JMI User')){
			cur_frm.set_df_property('regional_office', 'hidden', 1);
		}
		else {
			cur_frm.set_df_property('regional_office', 'hidden', 0);
		}
		if (cur_frm.doc.category_b == "Artisan"){
			cur_frm.set_df_property('entity_full_name', 'reqd', 0);
		}
		else{
			cur_frm.set_df_property('entity_full_name', 'reqd', 1);
		}

		if (cur_frm.doc.workflow_state == 'Draft' || frm.is_new()) {
			cur_frm.set_df_property('applicant_name','read_only', 0);
			cur_frm.set_df_property('middle_name','read_only', 0);
			cur_frm.set_df_property('last_name','read_only', 0);
			cur_frm.set_df_property('mobile_number','read_only', 0);
			cur_frm.set_df_property('email_id','read_only', 0);
		}
		else {
			if(! frappe.user_roles.includes('HO')){
				cur_frm.set_df_property('applicant_name','read_only' ,1);
				cur_frm.set_df_property('middle_name','read_only' ,1);
				cur_frm.set_df_property('last_name','read_only' ,1);
				cur_frm.set_df_property('mobile_number','read_only' ,1);
				cur_frm.set_df_property('email_id','read_only' ,1);
			}
			else {
				cur_frm.set_df_property('applicant_name','read_only', 0);
				cur_frm.set_df_property('middle_name','read_only', 0);
				cur_frm.set_df_property('last_name','read_only', 0);
				cur_frm.set_df_property('mobile_number','read_only', 0);
				cur_frm.set_df_property('email_id','read_only', 0);
			}
		}

		if( frappe.session.user !== 'Administrator' && frappe.user_roles.includes ('JMI User')){
			cur_frm.set_df_property('i_agree', 'read_only' ,0);
			cur_frm.set_df_property('documents_tab', 'hidden', 1);
			cur_frm.set_df_property('upload_agreement', 'hidden', 1);
			cur_frm.set_df_property('documents', 'hidden', 1);
		}
		else {
			cur_frm.set_df_property('i_agree','read_only' ,1);
			cur_frm.set_df_property('documents_tab', 'hidden', 0);
			cur_frm.set_df_property('upload_agreement', 'hidden', 0);
			cur_frm.set_df_property('documents', 'hidden', 0);
		}
		if (frappe.session.user !== 'Administrator' && frappe.user_roles.includes('Verification Officer(VO)') && (cur_frm.doc.workflow_state == 'Approved By HO' || cur_frm.doc.workflow_state == 'Approved By RO') ){
		    cur_frm.set_df_property('bondagreement','hidden',0);
		    if (cur_frm.doc.production_in_previous_year_verified){
		    	cur_frm.set_df_property('production_in_previous_year_verified','read_only',1);
		    }
		}
		let roles = frappe.user_roles;
		if(frappe.session.user != 'Administrator' &&  (cur_frm.doc.workflow_state == 'Approved By HO' || cur_frm.doc.workflow_state == 'Approved By RO')){
				cur_frm.set_df_property('gender','read_only',1);
				cur_frm.set_df_property('religion','read_only',1);
				cur_frm.set_df_property('category__scst_other_in_case_b_is_1','read_only',1);
				cur_frm.set_df_property('state','read_only',1);
				cur_frm.set_df_property('district','read_only',1);
				cur_frm.set_df_property('tahsil__taluka','read_only',1);
				cur_frm.set_df_property('townvillage','read_only',1);
				cur_frm.set_df_property('assign_to','read_only',1);
				cur_frm.set_df_property('address_line_1','read_only',1);
				cur_frm.set_df_property('address_line_2','read_only',1);
				cur_frm.set_df_property('address_line_3','read_only',1);
				cur_frm.set_df_property('pin_code','read_only',1);
				cur_frm.set_df_property('attach_sample_report','read_only',1);
				cur_frm.set_df_property('no_child_labor_emp_mfg_product','read_only',1);
				cur_frm.set_df_property('no_hazardous_chemical_used_mfg_product','read_only',1);
				cur_frm.set_df_property('njb_regi_no','read_only',1);
				cur_frm.set_df_property('aadhar_number','read_only',1);
				cur_frm.set_df_property('udyog_aadhar','read_only',1);
				cur_frm.set_df_property('pan_number','read_only',1);
				cur_frm.set_df_property('gst_number','read_only',1);
				cur_frm.set_df_property('gst_copy','read_only',1);
				cur_frm.set_df_property('identification_proof_is','read_only',1);
				cur_frm.set_df_property('photo','read_only',1);
				cur_frm.set_df_property('proof_of_address','read_only',1);
				cur_frm.set_df_property('identification_proof','read_only',1);
				cur_frm.set_df_property('aadhar_card_copy','read_only',1);
				cur_frm.set_df_property('upload_agreement','read_only',1);
		}
		if (frappe.session.user === 'Administrator'){
			cur_frm.set_df_property('state','read_only',1);
			cur_frm.set_df_property('district','read_only',1);
			cur_frm.set_df_property('tahsil__taluka','read_only',1);
			cur_frm.set_df_property('townvillage','read_only',1);
			cur_frm.set_df_property('assign_to','read_only',1);
			cur_frm.set_df_property('address_line_1','read_only',1);
			cur_frm.set_df_property('address_line_2','read_only',1);
			cur_frm.set_df_property('address_line_3','read_only',1);
			cur_frm.set_df_property('pin_code','read_only',1);
			cur_frm.set_df_property('applicant_name','read_only',0);
			cur_frm.set_df_property('middle_name','read_only',0);
			cur_frm.set_df_property('last_name','read_only',0);
			cur_frm.set_df_property('mobile_number','read_only',0);
			cur_frm.set_df_property('email_id','read_only',0);
		}
	},
	applicant_name: function(frm){
		var valid_name = validate_name(frm.doc.applicant_name)
		if(valid_name == true){
			cur_frm.set_value('applicant_name',"");
			frappe.throw('Please enter valid first name .');
		}
	},
	middle_name: function(frm){
		var valid_name = validate_name(frm.doc.middle_name)
		if(valid_name == true){
			cur_frm.set_value('middle_name',"");
			frappe.throw('Please enter valid middle name .');
		}
	},
	last_name: function(frm){
		var valid_name = validate_name(frm.doc.last_name)
		if(valid_name == true){
			cur_frm.set_value('last_name',"");
			frappe.throw('Please enter valid last name.');
		}
	},
	mobile_number: function(frm){
		if(frm.doc.mobile_number){
			if(isNaN(frm.doc.mobile_number)){
				frm.set_value('mobile_number', );
			}
			if(frm.doc.mobile_number.length>10) {
				frappe.msgprint('Phone Number Must be 10 Digits');
				frm.set_value('mobile_number', );
			}
		}
	},
	aadhar_number:function(frm){
		if(frm.doc.aadhar_number){
			if(isNaN(frm.doc.aadhar_number)){
				frm.set_value('aadhar_number', );
			}
			if(frm.doc.aadhar_number.length>12) {
				frappe.msgprint('Aadhar Number Must be 12 Digits');
				frm.set_value('aadhar_number', );
			}
		}
	},
	state: function(frm){
		cur_frm.set_value('district', );
	},
	district: function(frm){
		cur_frm.set_value('tahsil__taluka', );
	},
	select_terms: function (frm) {
		erpnext.utils.get_terms(frm.doc.select_terms, frm.doc, function (r) {
			if (!r.exc) {
				frm.set_value("terms", r.message);
			}
		});
	},
	attach_sample_report: function(frm){
		if(cur_frm.doc.attach_sample_report ===1){
			cur_frm.set_df_property('sample_report', 'hidden', 1);
		}
		if(cur_frm.doc.attach_sample_report == 0){
			cur_frm.set_df_property('sample_report', 'hidden', 0);
		}
	},
	category_b: function(frm) {
		change_field_properties(frm);
	},
	validate: function(frm) {
	    if(frm.doc.njb_regi_no && !validate_njb_number(frm.doc.njb_regi_no)){
	        frm.set_value('njb_regi_no', '');
	        frappe.throw(__('Invalid NJB Registration Number!'));
	    }
			if(frm.doc.udyog_aadhar && !validate_udayam_adhar(frm.doc.udyog_aadhar)){
				frm.set_value('udyog_aadhar', '');
				frappe.throw(__('Invalid Udayam Aadhar!'))
			}
	},
	save_next_1: function(frm){
		frm.call({
				doc: frm.doc,
				method: "save_next",
		}).then((m) => frm.scroll_to_field('textile_details_of_product'));
	},
	save_next_2: function(frm){
		frm.call({
				doc: frm.doc,
				method: "save_next",
		}).then((m) => frm.scroll_to_field('njb_regi_no'));
	},
	save_next_3: function(frm){
		frm.call({
				doc: frm.doc,
				method: "save_next",
		}).then((m) => frm.scroll_to_field('upload_agreement'));
	},


	save_submit: function(frm){

		frappe.run_serially([
			() => {
				// if(frm.doc.workflow_state == "Draft"){
				// 	frappe.call({
				// 		doc : frm.doc,
				// 		method: 'get_amount',
					
				// 		callback: function (r) {
				// 			console.log(r)
				// 			if(!r.exc){
				// 				var url = "/payment-confirmation?amount="+r.message
				// 				console.log(url)
				// 				window.open(url, '_blank');
				// 			}
				// 		}
				// 	});
				// }
			},
			() => {
				frm.call({
					doc: frm.doc,
					method: "save_submit",
				}).then((m) => reload_doc());
			}
		]);

		// frm.call({
		// 		doc: frm.doc,
		// 		method: "save_submit",
		// }).then((m) => reload_doc());
	},
	
	// on_submit: function(frm) {
	// 	frappe.call({
	// 		doc : frm.doc,
	// 		method: 'get_amount',
	// 		// args: {
	// 		// 	'category': frm.doc.category,
	// 		// },
	// 		callback: function (r) {
	// 			console.log(r)
	// 			if(!r.exc){
	// 				alert("ok")
	// 				var url = "/payment-confirmation?amount="+r.message
	// 				console.log(url)
	// 				window.open(url, '_blank');
	// 			}
	// 		}
	// 	});
	// }
});

frappe.ui.form.on('Details of Products', {
	fiber_content: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.fiber_content){
			if(row.fiber_content>100 || row.fiber_content<50){
				row.fiber_content = 0
				cur_frm.refresh_field("textile_details_of_product");
				frappe.throw("Fiber Content should be in Percentage, Greater than 50!");
			}
		}
	},
	approve: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.approve === 1 && row.reject === 1) {
			frappe.model.set_value(cdt, cdn, 'approve', 0);
			cur_frm.refresh_field('textile_details_of_product');
			frappe.throw('Only one checkbox can be checked at a time');
		}
	},
	reject: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.reject === 1 && row.approve === 1) {
			frappe.model.set_value(cdt, cdn, 'reject', 0);
			cur_frm.refresh_field('textile_details_of_product');
			frappe.throw('Only one checkbox can be checked at a time');
		}
	}
});

frappe.ui.form.on('Submission of Sample For Testing', {
	declared_fibre_content: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.declared_fibre_content){
			if(row.declared_fibre_content>100 || row.declared_fibre_content<50){
				row.declared_fibre_content = 0
				cur_frm.refresh_field("submission_of_sample_for_testing");
				frappe.throw("Fiber Content should be in Percentage, Greater than 50!");
			}
		}
	}
});
frappe.ui.form.on('Textile_Details of Production In Previous Year', {
	produced: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.produced < (row.sold + row.self_consumed)){
			frappe.throw("Produced Qty should be greater than or equal to Sold+Self Consumed!");
		}
	},
	sold: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.produced < (row.sold + row.self_consumed)){
			frappe.throw("Produced Qty should be greater than or equal to Sold+Self Consumed!");
		}
	},
	self_consumed: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.produced < (row.sold + row.self_consumed)){
			frappe.throw("Produced Qty should be greater than or equal to Sold+Self Consumed!");
		}
	}
});

frappe.ui.form.on('Details Of Procurement In Previous Year For Retailers', {
	procured: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.procured < (row.sold + row.stock)){
			frappe.throw("Procured Qty should be greater than or equal to Sold+Stock!");
		}
	},
	sold: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.procured < (row.sold + row.stock)){
			frappe.throw("Procured Qty should be greater than or equal to Sold+Stock!");
		}
	},
	stock: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if(row.procured < (row.sold + row.stock)){
			frappe.throw("Procured Qty should be greater than or equal to Sold+Stock!");
		}
	}
});
frappe.ui.form.on('Textile_Details of Production Units or Retailer Sales Outlets',{
	approve: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.approve === 1 && row.reject === 1) {
			frappe.model.set_value(cdt, cdn, 'approve', 0);
			cur_frm.refresh_field('textile_details_of_product');
			frappe.throw('Only one checkbox can be checked at a time');
		}
	},
	reject: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.reject === 1 && row.approve === 1) {
			frappe.model.set_value(cdt, cdn, 'reject', 0);
			cur_frm.refresh_field('textile_details_of_product');
			frappe.throw('Only one checkbox can be checked at a time');
		}
	}
});

function validate_name(name){
	if(name){
		var regName = /^[a-zA-Z ]+$/;
		if(!regName.test(name)){
			return true
		}
		else{
			return false
		}
	}
}

let set_filters = function(frm){
  frm.set_query('district', () => {
    return {
        filters: {
            state: frm.doc.state
        }
    }
  });
  frm.set_query('tahsil__taluka', () => {
    return {
        filters: {
            district: frm.doc.district
        }
    }
  });
	frm.set_query('pin_code', () => {
    return {
        filters: {
            state: frm.doc.state,
						district: frm.doc.district
        }
    }
  });
	frm.set_query('regional_office', () => {
    return {
				query: "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.regional_office_filter_query",
        filters: {
            state: frm.doc.state,
						district: frm.doc.district
        }
    }
  });
	frm.set_query("assign_to", "textile_details_of_production_units_or_retailer_sales_outlets", function(doc, cdt, cdn) {
		const row = locals[cdt][cdn];
		return {
			query: "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.set_assign_to",
		}
	});
	frm.set_query('assign_to', () => {
		return {
			query: "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.set_assign_to",
		}
	});
	frm.set_query("package_unit", "textile_details_of_product", function(doc, cdt, cdn) {
		let d = locals[cdt][cdn];
		return {
			query: "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.get_package_unit",
			filters: {'product_type': d.product_type}
		}
	});
}

let change_field_properties = function(frm){
	frm.set_df_property('documents', 'cannot_add_rows', true);
	frm.set_df_property('documents', 'cannot_delete_rows', true);
	frm.set_df_property('documents', 'cannot_delete_all_rows', true);
	if(cur_frm.doc.category_b==='Artisan'){
		artisan_field_property(frm);
	}
	else{
		cur_frm.set_df_property('category__scst_other_in_case_b_is_1','hidden',1);
	}
	if(cur_frm.doc.category_b ==="Manufacturer" ){
		manufacturer_field_property(frm);
	}

	if(cur_frm.doc.category_b ==="Retailer" ){
		retailer_field_property(frm);
	}

	if(cur_frm.doc.category_b ==="Manufacturer" || cur_frm.doc.category_b==="Retailer"){
		manufacturer_retailer_field_property(frm);
	}
	else {
		cur_frm.set_df_property('entity_full_name', 'hidden', 1);
	}

	if( frappe.session.user != 'Administrator' && frappe.user_roles.includes ('JMI User')){
		cur_frm.set_df_property('no_child_labor_emp_mfg_product', 'hidden', 1)
		cur_frm.set_df_property('no_hazardous_chemical_used_mfg_product', 'hidden', 1)
	}

}

let artisan_field_property = function(frm){
	cur_frm.set_df_property('gender','hidden',0);
	cur_frm.set_df_property('religion','hidden',0);
	cur_frm.set_df_property('category__scst_other_in_case_b_is_1','hidden',0);
	cur_frm.set_df_property('certificate_of_registration__in_case_b_is_2_or_3','hidden',1);
	cur_frm.set_df_property('pan_card_copy','hidden',1);
	cur_frm.set_df_property('udyog_aadhar_copy','hidden',1);
	cur_frm.set_df_property('gst_copy','hidden',1);
	cur_frm.set_df_property('udyog_aadhar','hidden',1);
	cur_frm.set_df_property('pan_number','hidden',1);
	cur_frm.set_df_property('gst_number','hidden',1);
	cur_frm.set_df_property('details_of_production_unitsretailer_sales_outlets_section','hidden',1);
	cur_frm.set_df_property('identification_proof','hidden',0);
	cur_frm.set_df_property('identification_proof_is','hidden',0);
	cur_frm.set_df_property('aadhar_number','hidden',0);
	cur_frm.set_df_property('aadhar_card_copy','hidden',0);
	cur_frm.set_df_property('applicant_name', 'read_only', 0);
	cur_frm.set_df_property('middle_name', 'read_only', 0);
	cur_frm.set_df_property('last_name', 'read_only', 0);
	cur_frm.set_df_property('mobile_number', 'read_only', 0);
	cur_frm.set_df_property('email_id', 'read_only', 0);
	if(frm.doc.workflow_state == 'Draft'){
		cur_frm.set_df_property('aadhar_number',"reqd", true);
		cur_frm.set_df_property('aadhar_card_copy',"reqd", true);
	}
}

let manufacturer_field_property = function(frm){
	if(frm.doc.workflow_state == 'Draft'){
		cur_frm.set_df_property('udyog_aadhar', "reqd", 1);
		cur_frm.set_df_property('udyog_aadhar_copy', "reqd", 0);
	}
	cur_frm.set_df_property('aadhar_number', 'hidden', 1);
	cur_frm.set_df_property('aadhar_card_copy', 'hidden', 1);
	cur_frm.set_df_property('udyog_aadhar', 'hidden', 0);
	cur_frm.set_df_property('udyog_aadhar_copy', 'hidden', 0);
}

let retailer_field_property = function(frm){
	cur_frm.set_df_property('details_of_production_in_previous_year_section','hidden',1);
	cur_frm.set_df_property('aadhar_number', 'hidden', 1);
	cur_frm.set_df_property('aadhar_card_copy', 'hidden', 1);
	cur_frm.set_df_property('udyog_aadhar', 'hidden', 0);
	cur_frm.set_df_property('udyog_aadhar_copy', 'hidden', 0);
}

let manufacturer_retailer_field_property = function(frm){
	cur_frm.set_df_property('certificate_of_registration__in_case_b_is_2_or_3','hidden',0)
	cur_frm.set_df_property('pan_card_copy','hidden',0)
	cur_frm.set_df_property('udyog_aadhar_copy','hidden',0);
	cur_frm.set_df_property('gst_copy','hidden',0);
	cur_frm.set_df_property('identification_proof','hidden',1);
	cur_frm.set_df_property('identification_proof_is','hidden',1);
	cur_frm.set_df_property('textile_details_of_production_units_or_retailer_sales_outlets','hidden',0);
	cur_frm.set_df_property('gender','hidden',1);
	cur_frm.set_df_property('religion','hidden',1);
	cur_frm.set_df_property('udyog_aadhar','hidden',0);
	cur_frm.set_df_property('pan_number','hidden',0);
	cur_frm.set_df_property('gst_number','hidden',0);
	cur_frm.set_df_property('aadhar_number','hidden',1);
	cur_frm.set_df_property('aadhar_card_copy','hidden',1);
	cur_frm.set_df_property('entity_full_name', 'hidden', 0);
	cur_frm.set_df_property('entity_full_name', 'read_only', 0);
	cur_frm.set_df_property('applicant_name', 'read_only', 0);
	cur_frm.set_df_property('middle_name', 'read_only', 0);
	cur_frm.set_df_property('last_name', 'read_only', 0);
	cur_frm.set_df_property('mobile_number', 'read_only', 0);
	cur_frm.set_df_property('email_id', 'read_only', 0);
}

function validate_njb_number(njb_number) {
	let regex = new RegExp(/^[A-Z]{3}[0-9]{2}[A-Z]{3}[0-9]{9}$/);
	if (njb_number === null) {
		return 0;
	}
	if (regex.test(njb_number) === true) {
		return 1;
	}
	else {
		return 0;
	}
}
function validate_udayam_adhar(udyog_aadhar){
	let regex = new RegExp(/^^[A-Z]{6}-[A-Z]{2}-[0-9]{2}-[0-9]{7}$/);
	if(udyog_aadhar == null){
		return 0;
	}
	if (regex.test(udyog_aadhar) == true){
		return 1;
	}
	else{
		return 1;
	}
}
function make_fields_mandatory(frm){
	cur_frm.fields_dict.documents.grid.toggle_reqd
    ("upload_test_report", frm.doc.workflow_state === "Assigned VO")

    /*cur_frm.fields_dict.documents.grid.toggle_reqd
    ("upload_test_report", frm.doc.workflow_state === "Save")*/

	if(frm.doc.workflow_state == 'Application Submitted')
	{
		if(frm.doc.category_b == 'Artisan'){
			cur_frm.set_df_property('assign_to', "reqd", true);
		}
	}
	let workflow_states = ['Draft', 'Application Submitted','Re-Assign'];
	if(!workflow_states.includes(frm.doc.workflow_state))
	{
		var fields = [];
		var artisan_fields = ['regional_office', 'religion', 'gender', 'category__scst_other_in_case_b_is_1', 'textile_details_of_product', 'identification_proof_is', 'aadhar_number']
		var retailer_fields = ['regional_office', 'entity_full_name', 'textile_details_of_product', 'textile_details_of_production_units_or_retailer_sales_outlets', 'udyog_aadhar', 'pan_number', 'gst_number']
		var manufacturer_fields = ['regional_office', 'entity_full_name', 'textile_details_of_product', 'textile_details_of_production_units_or_retailer_sales_outlets',  'udyog_aadhar', 'pan_number', 'gst_number']

		if(frm.doc.category_b == 'Artisan'){
			fields = artisan_fields;
		}
		if(frm.doc.category_b == 'Retailer'){
			fields = retailer_fields;
		}
		if(frm.doc.category_b == 'Manufacturer'){
			fields = manufacturer_fields;
		}
		$.each(fields, function(i, field) {
			if(!frm.doc[field]){
				cur_frm.set_df_property(field, "reqd", true);
			}
		});
	}
}

let change_button_properties = function(frm){
	let workflow_states = ['Draft', 'Application Submitted'];
	if(!workflow_states.includes(frm.doc.workflow_state)){
		cur_frm.set_df_property('save_next_1', 'hidden', 1);
		cur_frm.set_df_property('save_next_2', 'hidden', 1);
		cur_frm.set_df_property('save_next_3', 'hidden', 1);
		cur_frm.set_df_property('save_submit', 'hidden', 1);
	}
	$(".actions-btn-group").hide();
}
