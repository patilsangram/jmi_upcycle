// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pincode', {
	refresh: function(frm) {
    set_filters(frm);
	}
});

let set_filters = function(frm){
  frm.set_query('district', () => {
    return {
        filters: {
            state: frm.doc.state
        }
    }
  });
}
