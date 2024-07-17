frappe.label_status_page = {
    body: `<div class="widget-group ">
        <div class="widget-group-head">
            <div class="widget-group-control"></div>
        </div>
        <div class="widget-group-body grid-col-3">
            <div class="widget number-widget-box" data-widget-name="Total Count Of Labels">
                <div class="widget-head">
                    <div class="widget-label">
                        <div class="widget-title">
                            <span class="ellipsis" title="Total Allocated Labels">Total Count Of Labels</span>
                        </div>
                        <div class="widget-subtitle"></div>
                    </div>
                    <div class="widget-control">
                        <div class="card-actions dropdown pull-right"></div>
                    </div>
                </div>
                <div class="widget-body">
                    <div class="widget-content">
                        <div class="number" style="color:undefined" id="total_labels"> 0 </div>
                    </div>
                </div>
            </div>
        </div>
    </div>`
};

frappe.pages['labels-count'].on_page_load = function(wrapper) {
    new MyPage(wrapper);
};

var MyPage = Class.extend({
    init: function(wrapper) {
        this.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: 'Labels Count',
            single_column: true
        });
        this.make();
    },
    make: function() {
        var me = this;

        frappe.dom.freeze("Loading..."); // Add loading message while fetching data

        $(frappe.render_template(frappe.label_status_page.body, this))
            .appendTo(this.page.main);

        var total_labels = function() {
            frappe.call({
                method: "jute_mark_india.jute_mark_india.page.labels_count.labels_count.get_label_count",
                args: {
                    'user': frappe.session.user
                },
                callback: function(r) {
                    if (r.message) {
                        var totalLabelElement = document.getElementById("total_labels");
                        if (totalLabelElement) {
                            totalLabelElement.innerHTML = r.message;
                        }
                    }
                    frappe.dom.unfreeze(); // Remove loading message after data is loaded
                }
            });
        };
        total_labels();
    }
});
