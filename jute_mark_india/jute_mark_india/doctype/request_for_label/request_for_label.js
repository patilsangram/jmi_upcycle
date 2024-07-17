// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Request for Label', {
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

    if(frm.is_new()){
      frm.set_value('requested_by', frappe.session.user)
    }
		add_custom_buttons(frm);
		add_ro_trnsfer_buttons(frm);

	},

	remarks: function(frm) {
		jute_mark_india.validator.field_validate("remarks");
	},

	entity_full_name: function(frm) {
		jute_mark_india.validator.field_validate("entity_full_name");
	},

	requested_by :function(frm){
		if (frappe.user.has_role("Regional Officer(RO)")){
			frm.set_value('is_ro',1)
		}
		frappe.call({
			 method : 'jute_mark_india.jute_mark_india.doctype.request_for_label.request_for_label.set_regional_office',
			 args :{
				 'user' : frm.doc.requested_by
			 },
			 callback : function(r) {
          frm.set_value("regional_office", r.message);
       }
			}); 

	}
});

let add_custom_buttons = function(frm){
	if(frm.doc.docstatus == 1 && frappe.user_roles.includes('Regional Officer(RO)')){
		frappe.call({
			 method : 'jute_mark_india.jute_mark_india.doctype.request_for_label.request_for_label.is_label_allocation_exist',
			 args :{
				 'request_for_label' : frm.doc.name,
				 'qty' : frm.doc.required_qty
			 },
			 callback : (r) => {
				 if(!r.message){
					 frm.add_custom_button('Create Label Allocation', () => {
			 			frappe.model.open_mapped_doc({
			 				method: 'jute_mark_india.jute_mark_india.doctype.request_for_label.request_for_label.create_label_allocation',
			 				frm: cur_frm
			 			})
			 		});
				 }
			 }
		});
	}
}


let add_ro_trnsfer_buttons = function(frm) {
	if(frm.doc.docstatus == 1 && frappe.session.user == "Administrator")
	{
		frappe.call({
			 method : 'jute_mark_india.jute_mark_india.doctype.request_for_label.request_for_label.is_label_allocation_exist',
			 args :{
				 'request_for_label' : frm.doc.name,
				 'qty' : frm.doc.required_qty
			 },
			 callback : (r) => {
				 if(!r.message){
					frm.add_custom_button('Transfer Label From RO', () => {
						frappe.model.open_mapped_doc({
			 				method: 'jute_mark_india.jute_mark_india.doctype.request_for_label.request_for_label.create_ro_transfer',
			 				frm: cur_frm
			 			})
			 		});
				}
			}
		});
	}
}
