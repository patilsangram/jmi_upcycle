frappe.listview_settings['Request for Label'] = {
    add_fields: ["allocated_percentage"],
    get_indicator:function(doc){
        if (!doc.docstatus) {
            return [__("Draft"), "red"];
        }
        else if(flt(doc.allocated_percentage) < 100 && flt(doc.allocated_percentage) > 0) {
            return [__("Partially Allocated"), "orange"];
        }
        else if(flt(doc.allocated_percentage) >= 100){
            return [__("Allocated"), "green"];
        }
        else {
            return [__("Not Allocated"), "blue"];
        }
    }
}