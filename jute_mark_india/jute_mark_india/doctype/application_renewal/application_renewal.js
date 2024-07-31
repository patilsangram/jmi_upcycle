// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Application Renewal', {
	refresh:function(frm) {
		frm.add_custom_button('Make Payment', function() {
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
					workflow_state: ['in', ['Approved By HO', 'Approved By RO']]
				}
			}
		});

		frm.set_query("assign_to", "assign_vo_for_sites", function(doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				query: "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.set_assign_to",
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
				const date = new Date();
				let currentDay= String(date.getDate()).padStart(2, '0');
				let currentMonth = String(date.getMonth()+1).padStart(2,"0");
				let currentYear = date.getFullYear();
				// we will display the date as DD-MM-YYYY 
				//let currentDate = `${currentDay}-${currentMonth}-${currentYear}`;
				let currentDate = `${currentYear}-${currentMonth}-${currentDay}`;
				console.log("The current date is " + currentDate); 
				frm.set_value("renewal_date",currentDate)
			}
		}); 
	},

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
	},

	reason_for_enhancement: function(frm) {
		jute_mark_india.validator.field_validate("reason_for_enhancement");
	}
});
