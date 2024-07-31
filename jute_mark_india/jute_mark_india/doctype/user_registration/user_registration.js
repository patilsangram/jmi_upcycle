// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('User Registration', {
	refresh: function(frm) {
    frm.disable_save();
    frm.disable_form();
	}
});
