// Copyright (c) 2023, tech4all Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price List Setting', {
	refresh: function(frm) {
		frm.add_custom_button("Add Price List", function() {
			frappe.set_route("Form", "Price List", "new");
		});
		frm.add_custom_button("Change Price List Items Rate", function(frm) {
			let dialog = new frappe.ui.Dialog({
				title: "Update Price List Items Rate",
				fields: [
					{
						label: 'Price List',
						fieldname: 'price_list',
						fieldtype: 'Link',
						options: 'Price List'
					},
					{
						label: 'Rate',
						fieldname: 'price_list_rate',
						fieldtype: 'Currency',
						options: 'currency',

					}
				],
				size: 'small',
				primary_action_label: 'Submit',
				primary_action(values) {
					frappe.call({
						method: "tech4all_pos_general.tech4all_pos_general.doctype.price_list_setting.price_list_setting.update_price_list_rate",
						args: {
							price_list: values.price_list,
							rate: values.price_list_rate,
						},
						callback: function() {
							cur_frm.reload_doc();
						}
					});
					dialog.hide();
				}
			});

			dialog.show();
		});
	}
});
