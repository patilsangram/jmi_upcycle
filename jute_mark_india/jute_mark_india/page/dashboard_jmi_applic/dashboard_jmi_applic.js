frappe.pages['dashboard-jmi-applic'].on_page_load = function(wrapper) {
    new MyPage(wrapper);
};

MyPage = Class.extend({    
    init: function(wrapper) {
        this.page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Application & Label Status',
        single_column: true
    });
    this.make(wrapper);
    this.setup(wrapper);

    },
    setup:function(wrapper){
        var me = this;
        this.elements = {
            layout: $(wrapper).find(".layout-main-section-wrapper"),
        };
        
        this.elements.map_wrapper = $('<div class="col layout-main-section-wrapper" id="geomap" style="float:left; width: 50%; height: 72vh;"></div>')
            .appendTo(this.elements.layout);
        this.elements.chart_wrapper = $('<div class="col layout-main-section-wrapper" id="geochart" style="float:right;width:50%; position =relative; display: grid;grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));grid-gap: 5px;"></div>')
            .appendTo(this.elements.layout);
        this.elements.state_warpper = $('<div class="col layout-main-section-wrapper" id="state_list" style="float:left;width:50%; position =relative; display: grid;grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));"></div>').appendTo(this.elements.layout);
        
        this.elements.chart_wrapper.html(this.chart_regi())
        this.elements.state_warpper.html(this.state_chart())
        this.elements.map_wrapper.html(this.get_table_css()) 


        frappe.call({
            method: "jute_mark_india.jute_mark_india.page.dashboard_jmi_applic.dashboard_jmi_applic.get_overall_data",   
            callback: function(r) {
                if(r.message) 
                {
                    var table12 = document.getElementById("table12");
                    var data = r.message[0];      
                    let row = table12.insertRow(1);
                    let c1 = row.insertCell(0);
                    let c2 = row.insertCell(1);
                    let c3 = row.insertCell(2);
                    let c4 = row.insertCell(3);
                    let c5 = row.insertCell(4);
                    let c6 = row.insertCell(5);
                    let c7 = row.insertCell(6);
                    let c8 = row.insertCell(7);
                    c1.innerText = data.application_received
                    c2.innerText = data.registered_application
                    c3.innerText = data.sc_application
                    c4.innerText = data.st_application
                    c5.innerText = data.other_cast_application
                    c6.innerText = data.male_application
                    c7.innerText = data.female_application
                    c8.innerText = data.other_gender_application
                    
                    var table13 = document.getElementById("table13");
                    var data1 = r.message[1]
                    let row1 = table13.insertRow(1);
                    let c21 = row1.insertCell(0);
                    let c22 = row1.insertCell(1);
                    let c23 = row1.insertCell(2);
                    let c24 = row1.insertCell(3);
                    let c25 = row1.insertCell(4);
                    let c26 = row1.insertCell(5);
                    let c27 = row1.insertCell(6);
                    c21.innerText = data1.sold_labels
                    c22.innerText = data1.sc_labels
                    c23.innerText = data1.st_labels
                    c24.innerText = data1.other_cast_labels
                    c25.innerText = data1.male_labels
                    c26.innerText = data1.female_labels
                    c27.innerText = data1.other_gender_labels
                }
            }
        })
        frappe.call({
            method: "jute_mark_india.jute_mark_india.page.dashboard_jmi_applic.dashboard_jmi_applic.get_state_wise_data",   
            callback: function(r) {
                if(r.message) 
                {
                    var table5 = document.getElementById("table5");
                    adding_state_data(table5, r.message)
                }
            }
        })
        function adding_state_data(table,data)
        {
            data.forEach(function (profile, index, arr) {
                let row = table.insertRow(-1);
                let c1 = row.insertCell(0);
                let c2 = row.insertCell(1);
                let c3 = row.insertCell(2);
                let c4 = row.insertCell(3);
                let c5 = row.insertCell(4);
                let c6 = row.insertCell(5);
                c1.innerText = profile.state
                c2.innerText = profile.application_received
                c3.innerText = profile.verification_pending
                c4.innerText = profile.registered_application
                c5.innerText = profile.rejected_application
                c6.innerText = profile.approval_pending

                if (profile.state == 'Total') {
                    console.log("total row")
                    $(row).css("font-weight", "bold")
                }
            });
        }
        refresh_btn: wrapper.page.set_primary_action(__("Refresh"),
                function() { location.reload(); }, "fa fa-refresh")           
    },
    make: function(wrapper) {
        Promise.all([

            this.loadScript("https://cdn.anychart.com/releases/8.11.1/js/anychart-base.min.js"),
            this.loadScript("https://cdn.anychart.com/releases/8.11.1/js/anychart-core.min.js"),
            this.loadScript("https://cdn.anychart.com/releases/8.11.1/js/anychart-bundle.min.js"),
            this.loadScript("https://cdn.anychart.com/releases/8.11.1/js/anychart-map.min.js"),
            this.loadScript("https://cdn.anychart.com/geodata/2.1.1/countries/india/india.js")
             ]).then(() => {
                this.initializeMap();
            /*setTimeout(() => {
                this.initializeMap();
                }, 3000);*/
             })
             .catch((error) => {
                console.error("Error loading AnyChart scripts:", error);
            });
    },
    loadScript: function(url) {
        return new Promise((resolve, reject) => {
            var script = document.createElement("script");
            script.src = url;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
         });
    },
	initializeMap: function() 
    {    
        var map = anychart.map();
        map.interactivity().selectionMode('single-select');  
        var data 
        frappe.call({
			method: "jute_mark_india.jute_mark_india.page.dashboard_jmi_applic.dashboard_jmi_applic.get_total_application",	
			callback: function(r) {
				if(r.message) 
                {
					data = r.message
                    var dataSet = anychart.data.set(data);
                    series = map.choropleth(dataSet);
                    series.geoIdField('id');

                    // tooltip
                    var tooltip = map.getSeries(0).tooltip();
                    tooltip.format("Reg.Users. {%value}");

                    // set map color settings
                    // series.colorScale(anychart.scales.linearColor('#deebf7', '#3182bd'));
                    series.hovered().fill('#addd8e');
                    // set geo data, you can find this map in our geo maps collection
                    // https://cdn.anychart.com/#maps-collection
                    map.geoData(anychart.maps['india']);
                    map.container('geomap'); // Set your container ID here
                    map.draw();
                    map.listen('pointsSelect', function (e) 
                    {
                        var selectedPoint = e.seriesStatus[0].points;
                        document.getElementById("table12").deleteRow(1);
                        document.getElementById("table13").deleteRow(1);
                        frappe.call({
                            method: "jute_mark_india.jute_mark_india.page.dashboard_jmi_applic.dashboard_jmi_applic.get_overall_data",
                            args:{
                                'state':selectedPoint[0]['properties']['name']
                            },   
                            callback: function(r) {
                                if(r.message) 
                                {
                                    var table = document.getElementById("table12");
                                    var data = r.message[0];  
                                    let row = table.insertRow(1);
                                    let c1 = row.insertCell(0);
                                    let c2 = row.insertCell(1);
                                    let c3 = row.insertCell(2);
                                    let c4 = row.insertCell(3);
                                    let c5 = row.insertCell(4);
                                    let c6 = row.insertCell(5);
                                    let c7 = row.insertCell(6);
                                    let c8 = row.insertCell(7);
                                    c1.innerText = data.application_received
                                    c2.innerText = data.registered_application
                                    c3.innerText = data.sc_application
                                    c4.innerText = data.st_application
                                    c5.innerText = data.other_cast_application
                                    c6.innerText = data.male_application
                                    c7.innerText = data.female_application
                                    c8.innerText = data.other_gender_application
                                    var table13 = document.getElementById("table13");
                                    var data1 = r.message[1]
                                    let row1 = table13.insertRow(1);
                                    let c21 = row1.insertCell(0);
                                    let c22 = row1.insertCell(1);
                                    let c23 = row1.insertCell(2);
                                    let c24 = row1.insertCell(3);
                                    let c25 = row1.insertCell(4);
                                    let c26 = row1.insertCell(5);
                                    let c27 = row1.insertCell(6);
                                    c21.innerText = data1.sold_labels
                                    c22.innerText = data1.sc_labels
                                    c23.innerText = data1.st_labels
                                    c24.innerText = data1.other_cast_labels
                                    c25.innerText = data1.male_labels
                                    c26.innerText = data1.female_labels
                                    c27.innerText = data1.other_gender_labels
                                }
                            }
                        });
                        frappe.call({
                            method: "jute_mark_india.jute_mark_india.page.dashboard_jmi_applic.dashboard_jmi_applic.get_state_details",
                            args:{
                                'state':selectedPoint[0]['properties']['name']
                            },   
                            callback: function(r) {
                                if(r.message) 
                                {
                                    var table1 = document.getElementById("table1");
                                    adding_data(table1,r.message[0])
                                    var table2 = document.getElementById("table2");
                                    adding_data(table2,r.message[1])
                                    var table3 = document.getElementById("table3");
                                    adding_data(table3,r.message[2])
                                    var table4 = document.getElementById("table4");
                                    adding_data(table4,r.message[3])
                            
                                    function adding_data(table,data)
                                    {
                                        let row = document.getElementById("row1")
                                        if (row){
                                            document.getElementById("row1").remove();
                                        }    
                                        data.forEach(function (profile, index, arr) {
                                            let row = table.insertRow(-1);
                                            let c1 = row.insertCell(0);
                                            let c2 = row.insertCell(1);
                                            let c3 = row.insertCell(2);
                                            let c4 = row.insertCell(3);
                                            let c5 = row.insertCell(4);
                                            let c6 = row.insertCell(5);
                                            c1.innerText = profile.regional_office
                                            c2.innerText = profile.application_received
                                            c3.innerText = profile.verification_pending
                                            c4.innerText = profile.registered_application
                                            c5.innerText = profile.rejected_application
                                            c6.innerText = profile.approval_pending
                                        });
                                    };
                                    var table6 = document.getElementById("table6");
                                    var data = r.message[4]
                                    let row = document.getElementById("row1")
                                    if (row){
                                        document.getElementById("row1").remove();
                                    }                            
                                    data.forEach(function (profile, index, arr) {
                                        let row = table6.insertRow(-1);
                                        let c1 = row.insertCell(0);
                                        let c2 = row.insertCell(1);
                                        let c3 = row.insertCell(2);
                                        let c4 = row.insertCell(3);
                                        let c5 = row.insertCell(4);
                                        let c6 = row.insertCell(5);
                                        let c7 = row.insertCell(6);
                                        c1.innerText = profile.regional_office
                                        c2.innerText = profile.cast
                                        c3.innerText = profile.application_received
                                        c4.innerText = profile.verification_pending
                                        c5.innerText = profile.registered_application
                                        c6.innerText = profile.rejected_application
                                        c7.innerText = profile.approval_pending
                                    });

                                    var table7 = document.getElementById("table7");
                                    var data = r.message[5]
                                    let row2 = document.getElementById("row1")
                                    if (row2){
                                        document.getElementById("row1").remove();
                                    }    
                                    data.forEach(function (profile, index, arr) {
                                        let row = table7.insertRow(-1);
                                        let c1 = row.insertCell(0);
                                        let c2 = row.insertCell(1);
                                        let c3 = row.insertCell(2);
                                        let c4 = row.insertCell(3);
                                        let c5 = row.insertCell(4);
                                        let c6 = row.insertCell(5);
                                        let c7 = row.insertCell(6);
                                        c1.innerText = profile.regional_office
                                        c2.innerText = profile.gender
                                        c3.innerText = profile.application_received
                                        c4.innerText = profile.verification_pending
                                        c5.innerText = profile.registered_application
                                        c6.innerText = profile.rejected_application
                                        c7.innerText = profile.approval_pending
                                    });

                                    var table8 = document.getElementById("table8");
                                    var data = r.message[6]
                                    let row3 = document.getElementById("row1")
                                    if (row3){
                                        document.getElementById("row1").remove();
                                        }    
                                    data.forEach(function (profile, index, arr) {
                                        let row = table8.insertRow(-1);
                                        let c1 = row.insertCell(0);
                                        let c2 = row.insertCell(1);
                                        let c3 = row.insertCell(2);
                                        let c4 = row.insertCell(3);
                                        let c5 = row.insertCell(4);
                                        let c6 = row.insertCell(5);
                                        let c7 = row.insertCell(6);
                                        c1.innerText = profile.regional_office
                                        c2.innerText = profile.religion
                                        c3.innerText = profile.application_received
                                        c4.innerText = profile.verification_pending
                                        c5.innerText = profile.registered_application
                                        c6.innerText = profile.rejected_application
                                        c7.innerText = profile.approval_pending
                                    });

                                    // var table9 = document.getElementById("table9");
                                    // adding_label_data(table9,r.message[7])
                                    // function adding_label_data(table,data)
                                    // {
                                    //     let row = document.getElementById("row1")
                                    //     if (row){
                                    //         document.getElementById("row1").remove();
                                    //     }    
                                    //     data.forEach(function (profile, index, arr) {
                                    //         let row = table.insertRow(-1);
                                    //         let c1 = row.insertCell(0);
                                    //         let c2 = row.insertCell(1);
                                    //         let c3 = row.insertCell(2);
                                    //         let c4 = row.insertCell(3);
                                    //         let c5 = row.insertCell(4);
                                            
                                    //         c1.innerText = profile.regional_office
                                    //         c2.innerText = profile.labels_in_stock
                                    //         c3.innerText = profile.requsted_labels
                                    //         c4.innerText = profile.delivered_labels
                                    //         c5.innerText = profile.remaining_for_order
                                            
                                    //     });
                                    // };
                                }
                            }           
                        });
                    });
	            }     	
            }
        })

    },

    chart_regi:function()
    {

    	return `<div id="div12" > <label class="" style="font-weight: bold;font-size:larger;color: chocolate"; >Application Status</label>
        <table class="stat_tables" id="table12">
            <thead>
                <tr>
                    <th class="text-left" >Total Application Received </th>  
                    <th class="text-left" >Total Registration Completed </th>
                    <th class="text-left" >SC</th>
                    <th class="text-left" >ST</th>
                    <th class="text-left">Other</th>
                    <th class="text-left">Male</th>
                    <th class="text-left">Female</th>
                   <th class="text-left">Other</th>                  
                </tr>
            </thead>
            <tbody>
                        <tr></tr>
            </tbody> 
           
        </table></div>

        <div id="div13" > <label class="" style="font-weight: bold;font-size:larger;color: chocolate"; >Label Sold Status</label>
        <table class="stat_tables"  id="table13">
            <thead>
                <tr>
                    <th class="text-left" >No. of Label Sold</th>  
                    <th class="text-left" >SC</th>
                    <th class="text-left" >ST</th>
                    <th class="text-left">Other</th>
                    <th class="text-left">Male</th>
                    <th class="text-left">Female</th>
                   <th class="text-left">Other</th>                  
                </tr>
            </thead>     
           <tbody>

           </tbody>
        </table></div>



        <div id="div1" > <label class="" style="font-weight: bold;font-size:larger;color: chocolate"; >Regional office wise Applications</label>
        <table class="stat_tables"  id="table1">
            <thead>
                <tr>
                    <th class="text-left" >Regional Office</th>  
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                   
                   
                </tr>
            </thead>
            <tbody>     
                    <tr id="row1">
                        <td class="text-left"  colspan =6><center> State is not selected </center></td>
                        
                        
                    </tr>
                
            </tbody>      
           
        </table></div>

        <div id="div3" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate"; >Manufacture</label>
        <table class="stat_tables"  id="table3">
            <thead>
                <tr>
                    <th class="text-left" >Regional Office</th>  
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                   
                </tr>
            </thead>
            <tbody>     
                    <tr id="row1">
                        <td class="text-left"  colspan =6><center> State is not selected </center></td>
                        
                        
                    </tr>
                
            </tbody>   
           
        </table></div>

        <div id="div4" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate"; >Retailer</label> <table class="stat_tables"  id="table4">
            <thead>
                <tr>
                    <th class="text-left" >Regional Office</th>               
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                   
                   
                </tr>
            </thead>

            <tbody>     
                    <tr id="row1">
                        <td class="text-left"  colspan =6><center> State is not selected </center></td>
                        
                        
                    </tr>
                
            </tbody>       
           
        </table></div>

        <div id="div2" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";>Artisan</label><table class="stat_tables"  id="table2">
            <thead>
                <tr>
                    <th class="text-left" >Regional Office</th>
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                   
                </tr>
            </thead>
            <tbody>     
                    <tr id="row1">
                        <td class="text-left"  colspan =6><center> State is not selected </center></td>
                        
                        
                    </tr>
                
            </tbody>
                
        </table></div>

        <div id="div6" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";>Artisan - Cast wise</label><table class="stat_tables"  id="table6">
            <thead>
                <tr>
                    <th class="text-left" >Regional Office</th>
                    <th class="text-left" >Cast</th>
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                    
                   
                </tr>
            </thead>
            <tbody>     
                    <tr id="row1">
                        <td class="text-left"  colspan =7><center> State is not selected </center></td>
                        
                        
                    </tr>
                
            </tbody>
                
        </table></div>

        <div id="div7" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";>Artisan - Gender wise</label><table class="stat_tables"  id="table7">
            <thead>
                <tr>
                    <th class="text-left" >Regional Office</th>
                    <th class="text-left" >Gender</th>
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                    
                   
                </tr>
            </thead>
            <tbody>     
                    <tr id="row1">
                        <td class="text-left"  colspan =7><center> State is not selected </center></td>
                        
                        
                    </tr>
                
            </tbody>
                
        </table></div>

        <div id="div8" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";>Artisan - Religion wise</label><table class="stat_tables"  id="table8">
            <thead>
                <tr>
                    <th class="text-left" >Regional Office</th>
                    <th class="text-left" >Religion</th>
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                    
                   
                </tr>
            </thead>
            <tbody>     
                    <tr id="row1">
                        <td class="text-left"  colspan =7><center> State is not selected </center></td>
                        
                        
                    </tr>
                
            </tbody>
                
        </table></div>`

        //label status hidden
        // <div><label class="control-label" style="font-weight: bold;font-size:larger;color: DodgerBlue";> LABEL STATUS</label>
        // <div id="div9" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";>Artisan</label>
        // <table class="stat_tables"  id="table9">
        //     <thead>
        //         <tr>
        //             <th class="text-left" >Regional Office</th>
        //             <th class="text-left" >Labels in Stock with RO</th>
        //             <th class="text-left" >Labels Indented</th>
        //             <th class="text-left" >Labels Delivered</th>
        //             <th class="text-left" >Order Remaining to Fulfill</th>
        //         </tr>
        //     </thead>
        //     <tbody>     
        //             <tr id="row1">
        //                 <td class="text-left"  colspan =7><center> State is not selected </center></td>
        //             </tr>
        //     </tbody>
        // </table></div>
        // <div id="div10" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";>Manufacture</label>
        // <table class="stat_tables"  id="table10">
        //     <thead>
        //         <tr>
        //             <th class="text-left" >Regional Office</th>
        //             <th class="text-left" >Labels in Stock with RO</th>
        //             <th class="text-left" >Labels Indented</th>
        //             <th class="text-left" >Labels Delivered</th>
        //             <th class="text-left" >Order Remaining to Fulfill</th>
        //         </tr>
        //     </thead>
        //     <tbody>     
        //             <tr id="row1">
        //                 <td class="text-left"  colspan =7><center> State is not selected </center></td>
        //             </tr>
        //     </tbody>
        // </table></div>
        // <div id="div11" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";> Retailer </label>
        // <table class="stat_tables"  id="table11">
        //     <thead>
        //         <tr>
        //             <th class="text-left" >Regional Office</th>
        //             <th class="text-left" >Labels in Stock with RO</th>
        //             <th class="text-left" >Labels Indented</th>
        //             <th class="text-left" >Labels Delivered</th>
        //             <th class="text-left" >Order Remaining to Fulfill</th>
        //         </tr>
        //     </thead>
        //     <tbody>     
        //             <tr id="row1">
        //                 <td class="text-left"  colspan =7><center> State is not selected </center></td>
        //             </tr>
        //     </tbody>
        // </table></div>
        // </div>
        
    },

    state_chart:function()
    {

        return `<div id="div1" > <label class="control-label" style="font-weight: bold;font-size:larger;color: chocolate";>STATE WISE JMI SCHEME STATUS</label>
        <table class="stat_tables"  id="table5">
            <thead>
                <tr>
                    <th class="text-left" >State</th>  
                    <th class="text-left" >Received App</th>
                    <th class="text-left" >Pending for Verification</th>
                    <th class="text-left" >Registered App</th>
                    <th class="text-left">Rejected App</th>
                    <th class="text-left">Pending for Approval / Rejection</th>
                   
                   
                </tr>
            </thead> 
            <tbody>
                <tr></tr>
            </tbody>   
           
        </table></div>`
    },
    
    get_table_css:function()
    {
        return `<style>
                    .stat_tables {
                        border-collapse: collapse;
                        width: 100%;
                    }
                    .anychart-credits{
                        display:None;
                    }
                    .stat_tables td, .stat_tables th {
                        border: 1px solid #000;
                        padding: 8px;
                        text-align: center;
                    }
                    .stat_tables th {
                        padding-top: 12px;
                        padding-bottom: 12px;
                        background-color: #dae8f4;
                    }
                    .page-body{
                        background-color:white;
                    }
                </style>`
    }

});


