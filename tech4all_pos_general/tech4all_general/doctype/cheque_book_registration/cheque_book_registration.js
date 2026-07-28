// Copyright (c) 2022, tech4all Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cheque Book Registration', {
	refresh: function(frm){
		if(frm.doc.docstatus == 1 && frm.doc.cheques_created==0){
			frm.add_custom_button("Create Cheques", function(){
				frm.trigger("create_cheques");
			}).addClass('btn btn-primary');
		}
	},
	create_cheques: function(frm) {
		frappe.call({
			method: "tech4all_pos_general.tech4all_pos_general.doctype.cheque_book_registration.cheque_book_registration.create_cheque",
			args: {
				"chequebook":frm.doc.name,
				"series_from":frm.doc.series_from,
				"number_of_leafs":frm.doc.number_of_leafs,
				"bank_account":frm.doc.bank_account,
				"company":frm.doc.company,
				"bank_name":frm.doc.bank_name,
				"dt":frm.doc.doctype,
				"dn":frm.doc.name

			},
			callback: function(r) {
				frm.reload_doc()
			}
		})
	},
});
