frappe.print_report = function (method, args){
	window.open(
		frappe.urllib.get_full_url(
			"/api/method/" + method +"?" +
			new URLSearchParams(args).toString()
		)
	);
	if (!w) {
		frappe.msgprint(__("Please enable pop-ups"));
		return;
	}
}