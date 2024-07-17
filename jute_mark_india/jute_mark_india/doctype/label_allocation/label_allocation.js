// Copyright (c) 2023, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Label Allocation', {
	refresh: function(frm) {
    set_filters(frm);
    frm.set_query('from_roll', () => {
      if (frm.doc.is_ro_transfer)
      {
        if(cur_frm.doc.from_ro_user){
          return {
              query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.complete_roll_ro_transfer',
              filters: {
              'user': cur_frm.doc.from_ro_user
              }
            }
          }
        else{
          frappe.throw("First select From RO User!!")
        }
      }
      else
      {
        return {
            query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_filter_complete_roll_selection',
          }
      }
    })

    frm.set_query('to_roll', () => {
      if (frm.doc.is_ro_transfer)
      {
        return {
          query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.complete_roll_ro_transfer',
            filters: {
            'user': cur_frm.doc.from_ro_user
            }
          }
      }
      else
      {
        return {
          query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_filter_complete_roll_selection',
        }
      }
    })

    frm.set_query('complete_roll_selection', () => {
    if (frm.doc.is_ro_transfer)
    {
      return {
        query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.complete_roll_ro_transfer',
          filters: {
          'user': cur_frm.doc.from_ro_user
          }
        }
    }
    else
    {
      return {
        query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_filter_complete_roll_selection',
        }
    }
    })
    
    frm.set_query('partial_roll_selection', () => {
      if (frm.doc.is_ro_transfer)
      {
        return {
          query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_filter_partial_ro_transfer',
          filters: {
              'user': cur_frm.doc.from_ro_user,
              'qty': Number(cur_frm.doc.requested_quantity)%2000
          }
        }

      }
      else
      {
        return {
            query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_filter_partial_selection',
            filters: {
                'qty': Number(cur_frm.doc.requested_quantity)%2000
            }
          }
      }
    })

    frm.set_query('from_ro_user', () => {
    return {
        query: 'jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_filter_from_ro_user',
        /*filters: {
            'user': Number(cur_frm.doc.requested_quantity)%2000
        }*/
      }
    })


	},

  // on_submit: function(frm) {
  //   if(frm.doc.is_paid == 1){
  //     frappe.msgprint("Payment Already Proceeded !")
  //   }else{
  //     frappe.call({
  //       doc : frm.doc,
  //       method: 'get_amount',
  //       // args: {
  //       // 	'category': frm.doc.category,
  //       // },
  //       callback: function (r) {
  //         console.log(r)
  //         if(!r.exc){
  //           alert("ok")
  //           var url = "/payment-confirmation?amount="+r.message+"&doctype="+frm.doc.doctype+"&docname="+frm.doc.name
  //           console.log(url)
  //           window.open(url, '_blank');
  //         }
  //       }
  //     });
  //   }
	// },

  
  from_roll:function(frm)
  {
    if (frm.doc.from_ro_user)
    {
      if(frm.doc.from_roll)
      {
        let rolls = parseInt(frm.doc.requested_quantity/2000);
        frappe.call({
          method: "jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_to_roll_ro_transfer",
            args: {
              'from_roll':frm.doc.from_roll,
              'no_of_rolls': rolls,
              'user':frm.doc.from_ro_user
            },
            callback: function(r) {
              frm.set_value("to_roll", r.message);
            }
        })
      }

    }
    else
    {
      if(frm.doc.from_roll)
      {
        let rolls = parseInt(frm.doc.requested_quantity/2000);
        frappe.call({
          method: "jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_to_roll",
            args: {
              'from_roll':frm.doc.from_roll,
              'no_of_rolls': rolls
            },
            callback: function(r) {
              frm.set_value("to_roll", r.message);
            }
        })
      }
    }
  },
  partial_roll_selection:function(frm)
  {
    if(frm.doc.partial_roll_selection)
    {
      frappe.call({
        method: "jute_mark_india.jute_mark_india.doctype.label_allocation.label_allocation.set_for_partial",
        args: {
          'roll':frm.doc.partial_roll_selection,
          'qty': (frm.doc.requested_quantity%2000)
        },
        callback: function(r) {
          frm.set_value("from_qr_code", r.message[0]);
          frm.set_value("to_qr_code", r.message[1]);
        }
      });
    }
  },

  from_ro_user :function(frm){
    frappe.call({
       method : 'jute_mark_india.jute_mark_india.doctype.request_for_label.request_for_label.set_regional_office',
       args :{
         'user' : frm.doc.from_ro_user
       },
       callback : function(r) {
          frm.set_value("from_ro_regional_office", r.message);
       }
      }); 

  },

});

let set_filters = function(frm) {
    
  frm.set_query('to_qr_code', () => {
    return {
      filters: {
        status: 'Available',
				name: ['>', frm.doc.from_qr_code]
      }
    }
  });
}
