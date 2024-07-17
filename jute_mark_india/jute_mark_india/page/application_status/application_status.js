frappe.pages['application-status'].on_page_load = function(wrapper) {
	new ApplicationStatus(wrapper);
};

var ApplicationStatus = Class.extend({
	init: function(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Application Status',
			single_column: true
		});

		this.page.main.addClass("frappe-card");
		this.page.body.append('<div class="as-table-area"></div>');
		this.$content = $(this.page.body).find(".as-table-area");

		this.make_filters();
		this.show_funnel_data();
	},

	make_filters: function() {
		var me = this
		this.reginal_office = this.page.add_field({
			label: __("Regional Office"),
			fieldname: "regional_office",
			fieldtype: "Link",
			options: "Regional Office",
			change: () => {
				me.show_funnel_data()
			}
		});

		this.from_date = this.page.add_field({
			label: __("From Date"),
			fieldname: "from_date",
			fieldtype: "Date",
			change: () => {
				me.show_funnel_data()
			}
		});

		this.to_date = this.page.add_field({
			label: __("To Date"),
			fieldname: "to_date",
			fieldtype: "Date",
			change: () => {
				me.show_funnel_data()
			}
		});

		this.category = this.page.add_field({
			label: __("Category"),
			fieldname: "category",
			fieldtype: "Select",
			options: ["", "Artisan", "Manufacturer", "Retailer"],
			change: () => {
				me.show_funnel_data()
			}
		});

		this.district = this.page.add_field({
			label: __("District"),
			fieldname: "district",
			fieldtype: "Link",
			options: "District",
			change: () => {
				me.show_funnel_data()
			}
		});

		this.refresh = this.page.add_field({
			label: __("Refresh"),
			fieldname: "refresh",
			fieldtype: "Button",
			click: () => {
				this.reginal_office.set_value("");
				this.from_date.set_value("");
				this.to_date.set_value("");
				this.category.set_value("");
				this.district.set_value("");
				me.show_funnel_data();
			},
		});
	},

	show_funnel_data: function() {
		var me = this;
		this.page.add_inner_message(__("Refreshing..."));
		filters = {
			"reginal_office": me.reginal_office.get_value(),
			"from_date": me.from_date.get_value(),
			"to_date": me.to_date.get_value(),
			"category": me.category.get_value(),
			"district": me.district.get_value()
		}
		frappe.call({
			method : "jute_mark_india.jute_mark_india.page.application_status.application_status.get_application_data",
			args: {"filters": filters},
			callback: function(r) {
				me.page.add_inner_message(__(""));
				me.$content.html(
					frappe.render_template('application_status', {
						data: r.message,
					})
				);
			}
		})
	}
})