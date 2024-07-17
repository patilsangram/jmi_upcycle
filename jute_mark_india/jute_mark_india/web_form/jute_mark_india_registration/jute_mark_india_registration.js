frappe.ready(function() {
  frappe.web_form.on('state', (field, value) =>{
    frappe.web_form.set_value("district", );
    frappe.web_form.set_value("tahsil__taluka", );
    frappe.web_form.set_value("pin_code", );
    frappe.call({
      method: 'jute_mark_india.jute_mark_india.web_form.jute_mark_india_registration.jute_mark_india_registration.get_districts',
      args: {
        state: value
      },
      freeze: true,
      callback: (r) => {
        var options = [];
        for (var i = 0; i < r.message.length; i++) {
          options.push({
            'label': r.message[i].name,
            'value': r.message[i].name
          });
        }
        var field = frappe.web_form.get_field("district");
        field._data = options;
        field.refresh();
      }
    });
  });

  frappe.web_form.on('district', (field, value) =>{
    frappe.call({
      method: 'jute_mark_india.jute_mark_india.web_form.jute_mark_india_registration.jute_mark_india_registration.get_tahsil_taluka',
      args: {
        district: value
      },
      freeze: true,
      callback: (r) => {
        var options = [];
        for (var i = 0; i < r.message.length; i++) {
          options.push({
            'label': r.message[i].name,
            'value': r.message[i].name
          });
        }
        var field = frappe.web_form.get_field("tahsil__taluka");
        field._data = options;
        field.refresh();
      }
    });
    frappe.call({
      method: 'jute_mark_india.jute_mark_india.web_form.jute_mark_india_registration.jute_mark_india_registration.get_pincodes',
      args: {
        district: value
      },
      freeze: true,
      callback: (r) => {
        var options = [];
        for (var i = 0; i < r.message.length; i++) {
          options.push({
            'label': r.message[i].name,
            'value': r.message[i].name
          });
        }
        var field = frappe.web_form.get_field("pin_code");
        field._data = options;
        field.refresh();
      }
    });
  });

  frappe.web_form.on('mobile_number', (field, value) =>{
    if(value){
      if(isNaN(value)){
        field.set_value('');
      }
      if(value.length>10) {
        frappe.msgprint('Phone Number Must be 10 Digits');
        field.set_value('');
      }
      frappe.call({
        method: 'jute_mark_india.jute_mark_india.web_form.jute_mark_india_registration.jute_mark_india_registration.validate_mobile_number',
        args: {
          mobile_no: value
        }
      });
    }
  });

  frappe.web_form.on('email_id', (field, value) =>{
    if(value){
      frappe.call({
        method: 'jute_mark_india.jute_mark_india.web_form.jute_mark_india_registration.jute_mark_india_registration.validate_email',
        args: {
          email_id: value
        }
      });
    }
  });

  frappe.web_form.on('aadhar_number', (field, value) =>{
    if(value){
      if(isNaN(value)){
        field.set_value('');
  		}
      if(value.length>12) {
        frappe.msgprint('Aadhar Number Must be 12 Digits');
        field.set_value('');
      }
    }
  });
});

frappe.web_form.validate = () =>{
    let udyog_aadhar = frappe.get_form.get_value('udyog_aadhar');
    var pattern = /^[A-Z]{6}-[A-Z]{2}-[0-9]{2}-[0-9]{7}$/
    if(!udyog_aadhar.match(pattern)){
      frappe.throw('Enter Valid Udayam Aadhar');
      return False;
    }
}
