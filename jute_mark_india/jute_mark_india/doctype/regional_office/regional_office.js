// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Regional Office', {
	address: function(frm) {
		jute_mark_india.validator.field_validate("address");
	}
});
