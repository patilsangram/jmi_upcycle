// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Site Schedule', {
	is_distance_150_km: function(frm) {
		console.log("in site Schedule")
		if(cur_frm.doc.is_distance_150_km ==="Yes"){cur_frm.set_df_property('enter_km','hidden',0)}
		if(cur_frm.doc.is_distance_150_km ==="No"){cur_frm.set_df_property('enter_km','hidden',1)}		
	}
});
