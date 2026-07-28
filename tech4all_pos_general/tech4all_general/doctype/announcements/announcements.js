// Copyright (c) 2023, tech4all Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Announcements', {
	refresh: function(frm){
		frm.trigger("display_on");
	},
	display_on: function(frm) {
		frm.set_df_property("from_date", "label", frm.doc.display_on == "Date" ? "On Date": "From Date" );

	}
});
