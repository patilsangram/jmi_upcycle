// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('On-Site Verification Form', {
	refresh: function(frm){
		if (frappe.user_roles.includes('HO')) {
			cur_frm.set_df_property('reviewed_the_onsite_verification_report_for_please_select', 'hidden', 0);
			cur_frm.set_df_property('label_entitlement_are', 'hidden', 0);
			cur_frm.set_df_property('office_remarks', 'hidden', 0);
			cur_frm.set_df_property('signature_with_name', 'hidden', 0);
			cur_frm.set_df_property('signature_preview', 'hidden', 0);
		}
		else if (frappe.user_roles.includes('Verification Officer(VO)')) {
			cur_frm.set_df_property('reviewed_the_onsite_verification_report_for_please_select', 'hidden', 1);
			cur_frm.set_df_property('office_remarks', 'hidden', 1);
			cur_frm.set_df_property('label_entitlement_are', 'hidden', 1);
			cur_frm.set_df_property('signature_with_name', 'hidden', 0);
			cur_frm.set_df_property('signature_preview', 'hidden', 0);
			
		}
		else if(frappe.user_roles.includes('Regional Officer(RO)')) {
			cur_frm.set_df_property('reviewed_the_onsite_verification_report_for_please_select', 'hidden', 0);
			cur_frm.set_df_property('label_entitlement_are', 'hidden', 0);
			cur_frm.set_df_property('office_remarks', 'hidden', 0);
			cur_frm.set_df_property('signature_with_name', 'hidden', 0);
			cur_frm.set_df_property('signature_preview', 'hidden', 0);
			
		}
		else  {
			cur_frm.set_df_property('reviewed_the_onsite_verification_report_for_please_select', 'hidden', 1);
			cur_frm.set_df_property('label_entitlement_are', 'hidden', 1);
			cur_frm.set_df_property('office_remarks', 'hidden', 1);
			cur_frm.set_df_property('signature_with_name', 'hidden', 1);
			cur_frm.set_df_property('signature_preview', 'hidden', 1);
		}
	},

	textile_registration_no: function(frm) {
		frappe.db.get_value('Jute Mark India Registration form',{'name':frm.doc.textile_registration_no},['aadhar_card_copy']).then(r => {
			frm.set_value('addhar_copy_from_regi',r.message.aadhar_card_copy)
		})
		frappe.db.get_value('Jute Mark India Registration form',{'name':frm.doc.textile_registration_no},['certificate_of_registration__in_case_b_is_2_or_3']).then(r => {
			frm.set_value('certificate_of_registration__in_case_b_is_2_or_3',r.message.certificate_of_registration__in_case_b_is_2_or_3)
		})
		frappe.db.get_value('Jute Mark India Registration form',{'name':frm.doc.textile_registration_no},['udyog_aadhar_copy']).then(r => {
			frm.set_value('prev_udyog_aadhar_copy',r.message.udyog_aadhar_copy)
		})
		frappe.db.get_value('Jute Mark India Registration form',{'name':frm.doc.textile_registration_no},['pan_card_copy']).then(r => {
			frm.set_value('prev_pan_card_copy',r.message.pan_card_copy)
		})
		frappe.db.get_value('Jute Mark India Registration form',{'name':frm.doc.textile_registration_no},['gst_copy']).then(r => {
			frm.set_value('prev_gst_copy',r.message.gst_copy)
		})
	},

	category_b:function (frm) {
		if(frm.doc.category_b == 'Artisan') {
			artisan_field_property(frm)
		}
		else {
			frm.set_df_property('category__scst_other_in_case_b_is_1','hidden',1);
		}
		if(frm.doc.category_b == "Manufacturer" || frm.doc.category_b == "Retailer") {
			manufacturer_retailer_field_property(frm);
		}
	},

	no_of_label_approved:function(frm) {
		if (frm.doc.no_of_label_approved > frm.doc.no_of_label_requested) {
			frappe.throw("No.of Label Approved must be less or equal to No.of Label requested")
		}
		if (frm.doc.no_of_label_approved>0 && frm.doc.no_of_label_approved<=frm.doc.no_of_labels) {
			frappe.throw("No.of Label Approved must be greater than No.of Label")
		}

		if (frm.doc.no_of_label_approved > 0) {
			frappe.call({
				method : 'jute_mark_india.jute_mark_india.doctype.on_site_verification_form.on_site_verification_form.set_label_check',
				args :{
					'app_id' : cur_frm.doc.textile_registration_no
				}
			});
		}
	},

	terms: function(frm) {
		jute_mark_india.validator.field_validate("terms");
	}
});

function artisan_field_property(frm) {
	cur_frm.set_df_property('gender','hidden',0);
	cur_frm.set_df_property('religion','hidden',0);
	cur_frm.set_df_property('category__scst_other_in_case_b_is_1','hidden',0);
	cur_frm.set_df_property('certificate_of_registration__in_case_b_is_2_or_3','hidden',1);
	cur_frm.set_df_property('prev_pan_card_copy','hidden',1);
	cur_frm.set_df_property('prev_udyog_aadhar_copy','hidden',1);
	cur_frm.set_df_property('prev_gst_copy','hidden',1);
	cur_frm.set_df_property('udyog_aadhar','hidden',1);
	cur_frm.set_df_property('pan_number','hidden',1);
	cur_frm.set_df_property('gst_number','hidden',1);
	cur_frm.set_df_property('textile_details_of_production_units_or_retailer_sales_outlets','hidden',1);
	cur_frm.set_df_property('identification_proof','hidden',0);
	cur_frm.set_df_property('identification_proof_is','hidden',0);
}

function manufacturer_retailer_field_property(frm) {
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
	cur_frm.set_df_property('addhar_copy_from_regi','hidden',1);
}

