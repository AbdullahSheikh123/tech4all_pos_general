frappe.ui.form.on("User", {
	refresh: function(frm){
		if(frappe.session.user == 'Administrator' ||	frappe.user_roles.includes("System Manager")){
			frm.add_custom_button(
				__("Login As"),
				function () {
					frappe.prompt(
						[
							{
								fieldtype: "Link",
								fieldname: "user",
								options: "User",
								label: __("Login as User"),
								reqd: 1,
							}
						],
						function (data) {
							frappe.call({
								method: "tech4all_pos_general.custom.user_custom.login_as_user",
								args: {
									user: data.user
								},
								callback: function(r){
									window.location.href = "/app";
								}
							});
						},
						__("Switch User Rights")
					);
				}
			);
		}
	}
});