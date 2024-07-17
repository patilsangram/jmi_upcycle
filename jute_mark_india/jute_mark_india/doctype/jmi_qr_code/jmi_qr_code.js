// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('JMI QR Code', {
	onload: function(frm) {
		change_field_properties(frm);
	},
	refresh: function(frm) {
		change_field_properties(frm);
	}
});

let change_field_properties = function(frm){
	if(frm.is_new()){
		frm.set_df_property('qr_code', 'hidden', 1);
    frm.set_df_property('sequence_number', 'read_only', 0);
	}
	else {
		frm.set_df_property('qr_code', 'hidden', 0);
    frm.set_df_property('sequence_number', 'read_only', 1);
		frm.disable_save();
	}
}
