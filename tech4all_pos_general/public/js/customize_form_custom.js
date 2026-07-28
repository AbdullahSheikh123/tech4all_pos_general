frappe.ui.form.on("Customize Form", {
	onload: function (frm) {
		frm.events.setup_export = setup_export;
	},
})

var setup_export = function(frm){
	if (frappe.boot.developer_mode) {
		frm.add_custom_button(
			__("Export Customizations"),
			function () {
				frappe.prompt(
					[
						{
							fieldtype: "Link",
							fieldname: "module",
							options: "Module Def",
							label: __("Module to Export"),
							reqd: 1,
						},
						{
							fieldtype: "Check",
							fieldname: "sync_on_migrate",
							label: __("Sync on Migrate"),
							default: 1,
						},
						{
							fieldtype: "Check",
							fieldname: "with_permissions",
							label: __("Export Custom Permissions"),
							default: 0,
						},
					],
					function (data) {
						frappe.call({
							method: "tech4all_pos_general.custom.customize_form_custom.export_customizations",
							args: {
								doctype: frm.doc.doc_type,
								module: data.module,
								sync_on_migrate: data.sync_on_migrate,
								with_permissions: data.with_permissions,
							},
						});
					},
					__("Select Module")
				);
			},
			__("Actions")
		);
	}
};