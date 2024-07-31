// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('JMI Appeal', {
  refresh: function(frm) {
    if(frm.is_new()){
      frm.set_value('user_id',frappe.session.user)
    }
    frm.set_query("assign_to", "assign_vo_for_sites", function(doc, cdt, cdn) {
    const row = locals[cdt][cdn];
    return {
        query: "jute_mark_india.jute_mark_india.doctype.jute_mark_india_registration_form.jute_mark_india_registration_form.set_assign_to",
    }
    });
		set_filters(frm);

    /*frm.set_query('assign_vo', function() {
      return {
        query: 'jute_mark_india.jute_mark_india.doctype.label_enhancement.label_enhancement.get_users'
      };
    });*/
	},
  jmi_appeal: function(frm){
    frm.call({
        doc: frm.doc,
        method: "get_application_for_esacalation",
    }).then((r) => set_application_details(frm, r.message));
  },
  application_no: function(frm){
    frappe.call({
      method: 'jute_mark_india.jute_mark_india.doctype.jmi_appeal.jmi_appeal.calculate_label_balance',
      args: {
        application_no: frm.doc.application_no,
        user: frappe.session.user
      },
      callback: function(r) {
        if (r.message) {
          var data = r.message
          frm.set_value("no_of_labels", data.no_of_labels)
          frm.set_value("labels_balance", data.label_balance)
          frm.refresh_fields();
        }
      }
    });
  },
  appeal_type:function(frm){
    frappe.call({
      method : 'jute_mark_india.jute_mark_india.doctype.jmi_appeal.jmi_appeal.get_registration_form_no',
      args :{
        'user' : frappe.session.user,
        'appeal_type' : frm.doc.appeal_type
      },
      callback : function(r) {
            frm.set_value("application_no", r.message);
        }
    }); 
  },
  application_remarks: function(frm) {
    jute_mark_india.validator.field_validate("application_remarks");
  }
});

let set_filters = function(frm){
  frm.set_query('application_no', () => {
    if(frm.doc.appeal_type){
      //if(frm.doc.appeal_type == 'Appeal for Rejection'){
        return {
          filters: {
            workflow_state: ['in', ['Rejected by HO', 'Rejected by RO']]
          }
        }
      }
      /*if(frm.doc.appeal_type == 'Appeal for Approval'){
        return {
          filters: {
            workflow_state: ['in', ['Approved By HO', 'Approved By RO']]
          }
        }
      }*/
    //}
    /*else{
      return {
        filters: {
          workflow_state: ['in', ['Approved By HO', 'Rejected by HO', 'Approved By RO', 'Rejected by RO']]
        }
      }
    }*/
  });
}

let set_application_details = function(frm, application_detatails){
  if(application_detatails){
    frm.set_value('application_no', application_detatails.application_no);
    frm.set_value('application_date', application_detatails.application_date);
    frm.set_value('applicant_name', application_detatails.applicant_name);
    frm.set_value('no_of_labels', application_detatails.no_of_labels);
    frm.refresh_fields()
  }
}
