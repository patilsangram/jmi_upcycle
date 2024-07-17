frappe.provide("jute_mark_india.validator");

jute_mark_india.validator.field_validate = function(field) {
	let input_str = cur_frm.doc[field]
	if (input_str && input_str != '' && input_str.length > 5) {
		var doc_ele = document.createElement('div');
		doc_ele.innerHTML = input_str;
		for (var c = doc_ele.childNodes, i = c.length; i--; ) {
			if (c[i].nodeType == 1) {
				cur_frm.set_value(field, "")
				cur_frm.refresh_field(field)
				frappe.msgprint("Input string contains HTML content")
			}
		}
	}
}
