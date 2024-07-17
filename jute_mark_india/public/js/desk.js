// dom ready
document.addEventListener("DOMContentLoaded", (event)=>{
  page_routing();
  setTimeout(()=>{
    improve_my_erp();
  }, 3000);
});

let improve_my_erp = () => {
	let improveBTN = document.createElement('a');
	improveBTN.classList = "btn btn-default btn-xs improve-my-erp";
	improveBTN.textContent = frappe.session.user_fullname;
  document.querySelector(".form-inline.fill-width.justify-content-end").prepend(improveBTN);
}

function page_routing(){
  var base_url = window.location.origin;
  frappe.call({
    method : 'jute_mark_india.jute_mark_india.utils.get_page_route',
    callback : function(r) {
        if(r.message){
          var new_url = base_url+r.message;
          redirect_paths = ["/app", "/app/home", "/"]
          if(redirect_paths.includes(window.location.pathname) && window.location.href != new_url){
            window.location.href = new_url
          }
        }
      }
  });
}

frappe.router.on('change', () => {
  route = frappe.get_route()
  if(route.length == 2 && !frappe.user_roles.includes("System Manager")){
      if (route[0] == "Workspaces"){
          $("#page-Workspaces .page-actions").html("")
      }
  }
})