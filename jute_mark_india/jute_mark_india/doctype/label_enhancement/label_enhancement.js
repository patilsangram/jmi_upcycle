// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Label Enhancement', {
	refresh:function(frm){
		if(frm.is_new()){
			frm.set_value('user_id',frappe.session.user)
		}
	    frm.set_query('on_site_verification', () => {
	      return {
	        filters: {
	          textile_registration_no: frm.doc.application_no
	        }
	      }
	    });

	     frm.set_query('application_no', () => {
	      return {
	        filters: {
	          workflow_state: ['in', ['Approved By HO', 'Approved By RO']],
	          email_id : frappe.session.user
	        }
	      }
	    });
	    frm.set_query("assign_to", "assign_vo_for_sites", function(doc, cdt, cdn) {
		const row = locals[cdt][cdn];
		return {
			query: "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.set_assign_to",
		}
	});
	    /*frm.set_query('assign_vo', function() {
			return {
				query: 'jute_mark_india.jute_mark_india.doctype.label_enhancement.label_enhancement.get_users'
			};
		});*/
	},

	// jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.regional_office_filter_query
	application_no: function(frm){
		if(!frm.doc.on_site_verification){
			frappe.call('jute_mark_india.api.mobile_api.get_on_site_verification_form', {
				application_no: frm.doc.application_no
			}).then(r => {
				if(r.message){
					frm.set_value('on_site_verification', r.message);
				}
				else {
					frappe.throw('On Site Verification form not yet created!')
				}
			});
		}
		frappe.call({
	      method: 'jute_mark_india.jute_mark_india.doctype.jmi_appeal.jmi_appeal.calculate_label_balance',
	      args: {
	        application_no: frm.doc.application_no,
	        user: frappe.session.user
	      },
	      callback: function(r) {
	        if (r.message) {
	        	//console.log("*******r=>",r.message)
	          var data = r.message
	          frm.set_value("total_label_as_per_prorata",data.no_of_labels)
	          frm.set_value("labels_balance", data.label_balance)
	          frm.refresh_fields();
	        }
	      }
	    });
	},
	user_id:function(frm){
		frappe.call({
			method : 'jute_mark_india.api.mobile_api.get_application_no',
			args :{
				'user' : frappe.session.user
			},
			callback : function(r) {
      			frm.set_value("application_no", r.message);
   			}
		}); 
	},

	reason_for_enhancement: function(frm) {
		jute_mark_india.validator.field_validate("reason_for_enhancement");
	}
});
