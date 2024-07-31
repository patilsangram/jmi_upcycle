frappe.listview_settings['JMI Appeal'] = {
	onload(listview) {
		if(frappe.route_options){
			if(frappe.session.user != 'Administrator' && frappe.user.has_role('HO')){
				frappe.route_options = {
					"appeal_type": ["=", "Appeal for Escalation"]
				}
			}		
		}	
	}
};
