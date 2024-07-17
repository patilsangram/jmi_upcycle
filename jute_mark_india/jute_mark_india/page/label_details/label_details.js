frappe.pages['label-details'].on_page_load = function(wrapper) {
	new MyPage(wrapper);
}
//PAGE CONTENT
MyPage = Class.extend({
	init:function(wrapper)
	{
		this.page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Label Status',
		single_column: true
		});
		this.make();

	},
	make:function()
	{
		let me = $(this);

		// body Content
		//let body = `<h1> Hellloooooooo</h1>`
		let total_labels = function()
		{
			frappe.call({
				method : "jute_mark_india.jute_mark_india.page.label_details.label_details.get_label_status",
				args: {
					'user':frappe.session.user
            	},
				callback : function(r)
				{
					var a = document.getElementById("total_labels")
					a.innerHTML = r.message[0]
					var b = document.getElementById("unused_labels")
					b.innerHTML = r.message[2]
					var c = document.getElementById("used_labels")
					c.innerHTML = r.message[1]
				}
			})
		}
		$(frappe.render_template(frappe.label_status_page.body,this)).appendTo(this.page.main)
		total_labels();
	}
})

//HTML Content
let body = `<div class="widget-group ">
				<div class="widget-group-head">
					
					<div class="widget-group-control"></div>
				</div>
				<div class="widget-group-body grid-col-3"><div class="widget number-widget-box" data-widget-name="Total Allocated Labels">
			<div class="widget-head">
				<div class="widget-label">
					<div class="widget-title"><span class="ellipsis" title="Total Allocated Labels">Total Allocated Labels</span></div>
					<div class="widget-subtitle"></div>
				</div>
				<div class="widget-control"><div class="card-actions dropdown pull-right">
			</div></div>
			</div>
			<div class="widget-body"><div class="widget-content">
				<div class="number" style="color:undefined" id="total_labels"> 0 </div>
				</div></div>


			<div class="widget-footer"></div>
		</div><div class="widget number-widget-box" data-widget-name="Balance Labels">
			<div class="widget-head">
				<div class="widget-label">
					<div class="widget-title"><span class="ellipsis" title="Balance Labels">Balance Labels</span></div>
					<div class="widget-subtitle"></div>
				</div>
				<div class="widget-control"><div class="card-actions dropdown pull-right">
				
			</div></div>
			</div>
			<div class="widget-body"><div class="widget-content">
				<div class="number" style="color:undefined" id="unused_labels"> 0 </div>
				</div></div>

			<div class="widget-footer"></div>
		</div><div class="widget number-widget-box" data-widget-name="Used Labels">
			<div class="widget-head">
				<div class="widget-label">
					<div class="widget-title"><span class="ellipsis" title="Used Labels">Used Labels</span></div>
					<div class="widget-subtitle"></div>
				</div>
				<div class="widget-control"><div class="card-actions dropdown pull-right">
				
			</div></div>
			</div>
			<div class="widget-body"><div class="widget-content">
				<div class="number" style="color:undefined" id="used_labels"> 0 </div>
				</div></div>
			<div class="widget-footer"></div>
			</div>
			</div>`;

frappe.label_status_page = {
	body:body
}
