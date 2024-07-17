// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('JMI QR Code Builder', {
	refresh: function(frm) {
    set_prerequisites(frm);
		make_generate_button(frm);
	}
});

let set_prerequisites = function(frm){
  //Get Constant Value from Settings
	if(!frm.doc.barcode_constant){
		frappe.db.get_single_value('QR Code Settings', 'qr_code_generation_constant').then( qr_code_generation_constant=>{
	    frm.set_value('barcode_constant', qr_code_generation_constant);
	  });
	}

	//Get Constant Value of qr_code_sequence_id from Settings
	if(!frm.doc.from_sequence_number){
		frappe.db.get_single_value('QR Code Settings', 'qr_code_sequence_id').then( qr_code_sequence_id=>{
			if(qr_code_sequence_id){
				frm.set_value('from_sequence_number', qr_code_sequence_id);
			}
			else{
				frm.set_value('from_sequence_number', '000000001');
			}
	  });
	}
	//Get Constant Value of roll_number from Settings
	if(!frm.doc.from_roll_number){
		frappe.db.get_single_value('QR Code Settings', 'roll_number').then( roll_number=>{
			if(roll_number){
				frm.set_value('from_roll_number', roll_number);
			}
			else{
				frm.set_value('from_roll_number', '000001');
			}
	  });
	}
}

let make_generate_button = function(frm){
	if(!frm.is_new() && frm.doc.status == 'Open' && frm.doc.docstatus==1){
		const btn = frm.add_custom_button("Generate QR Codes", () => {
			frm.call({
					doc: frm.doc,
					method: "generate_qr_codes",
					btn,
			}).then((m) => reload_doc());
		});
	}
}
