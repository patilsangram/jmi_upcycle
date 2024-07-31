// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Actual Site Visit Plan', {
	refresh: function(frm) {
		validate_km(frm);
		if(!frm.is_new() && (frm.doc.workflow_state!='Rejected by RO')){
			add_reschedule_button(frm);
		}
		if(frm.is_new() && !frm.doc.assigned_for){
			frm.set_value('assigned_for', frappe.session.user);
		}
		if(!frm.is_new() && frm.doc.visit_planed_on){
			cur_frm.set_df_property('visit_planed_on','read_only' ,1);
		}
	},
	distance_in_km: function(frm){
		validate_km(frm);
	},
	address_visited: function(frm) {
		jute_mark_india.validator.field_validate("address_visited");
	},
	commentsdiscussion_pointshighlights: function(frm) {
		jute_mark_india.validator.field_validate("commentsdiscussion_pointshighlights");
	},
	remarks_on_rejection: function(frm) {
		jute_mark_india.validator.field_validate("remarks_on_rejection");
	},
	next_stepway_forward: function(frm) {
		jute_mark_india.validator.field_validate("next_stepway_forward");
	}
});

let add_reschedule_button = function(frm){
	if(frm.doc.assigned_for){
		if(frm.doc.assigned_for == frappe.session.user){
			frm.add_custom_button('Re-Schedule', () => {
				make_reschedule_popup(frm);
			});
		}
	}
}

let make_reschedule_popup = function(frm){
	let d = new frappe.ui.Dialog({
    title: 'Enter details',
    fields: [
        {
            label: 'Rescheduled Date',
            fieldname: 'rescheduled_date',
            fieldtype: 'Date',
						reqd: 1
        }
    ],
    primary_action_label: 'Change',
    primary_action(values) {
	    rescheduled_site_visit(frm, values.rescheduled_date)
	    d.hide();
    }
	});
	d.show();
}

let rescheduled_site_visit = function(frm, rescheduled_date){
	frappe.call({
    method: 'jute_mark_india.jute_mark_india.doctype.actual_site_visit_plan.actual_site_visit_plan.rescheduled_site_visit',
    args: {
				site_visit_id: frm.doc.name,
        rescheduled_date: rescheduled_date
    },
    freeze: true,
		freeze_msg: 'Rescheduling...',
		callback: (r) => {
			frm.reload_doc();
    }
});
}

let validate_km = function(frm){
	if(frm.doc.distance_in_km){
		if (frm.doc.distance_in_km<0) {
			frm.set_value('distance_in_km', 0)
			frappe.throw('Distance in KM should be Greater than Zero')
		}
		if(frm.doc.distance_in_km>150){
			frm.set_value('is_distance_150_km', 'Yes')
		}
		else {
			frm.set_value('is_distance_150_km', 'No')
		}
	}
}
