frappe.ui.form.on('Payment Entry', {
	refresh: function(frm){
		if(frm.doc.docstatus == 0 && frm.doc.payment_type=="Pay" || frm.doc.payment_type=="Internal Transfer"){
            frm.add_custom_button("Attach Cheque", function(){
				frm.trigger("select_cheque");
			}).addClass('btn btn-primary');
		}
		else{
			frm.remove_custom_button("Attach Cheque");
		}
	},
	payment_type: function(frm){
		if(frm.doc.docstatus == 0 && frm.doc.payment_type=="Pay" || frm.doc.payment_type=="Internal Transfer" ){
            frm.add_custom_button("Attach Cheque", function(){
				frm.trigger("select_cheque");
			}).addClass('btn btn-primary');
			
		}
		else{
			frm.remove_custom_button("Attach Cheque");
		}
	},
    select_cheque: function(frm){
		if(!frm.doc.bank_account && frm.doc.payment_type=="Pay"){
			frappe.throw(__("Please select company bank account"))
		}

		if(!frm.doc.paid_from && frm.doc.payment_type=="Internal Transfer"){
			frappe.throw(__("Please select Account Paid From"))
		}


		if(frm.doc.bank_account && frm.doc.payment_type=="Pay"){
			var dialog = new frappe.ui.Dialog({
				title: __("Select Cheque"),
				fields: [
					{
						"fieldtype": "Link", "label": __("Cheque"),
						"fieldname": "cheque",
						"options": "Cheque",
						"reqd": 1,
						get_query: () => {
							return {
								query: "tech4all_pos_general.tech4all_pos_general.doctype.cheque.cheque.get_cheques",
								filters: {
									bank_account: frm.doc.bank_account,
									status: "Available",
									company: frm.doc.company
								}
							};
						}
					}
				],
				primary_action: function(){
					frm.set_value("reference_no", cur_dialog.get_value("cheque"));
					dialog.hide();
					frm.set_df_property("reference_no", "read_only", 1);
				}
			});
		}

		if(frm.doc.paid_from && frm.doc.payment_type=="Internal Transfer"){
			var bank_account = ""
			frappe.call({
				method:'tech4all_afm.custom.payment_entry_custom.get_cheque_list',
				args:{
					paid_from:frm.doc.paid_from
				},
				callback: function(r){
					if (r.message){
						bank_account = r.message
					}
					
					
				}
			});
			
			var dialog = new frappe.ui.Dialog({
				title: __("Select Cheque"),
				fields: [
					{
						"fieldtype": "Link", "label": __("Cheque"),
						"fieldname": "cheque",
						"options": "Cheque",
						"reqd": 1,
						get_query: () => {
							return {
								query: "tech4all_pos_general.tech4all_pos_general.doctype.cheque.cheque.get_cheques",
								filters: {
									// bank_account: frm.doc.paid_from,
									bank_account : bank_account,
									status: "Available",
									company: frm.doc.company
								}
							};
						}
					}
				],
				primary_action: function(){
					frm.set_value("reference_no", cur_dialog.get_value("cheque"));
					dialog.hide();
					frm.set_df_property("reference_no", "read_only", 1);
				}
			});
		}

		// var dialog = new frappe.ui.Dialog({
		// 	title: __("Select Cheque"),
		// 	fields: [
		// 		{
		// 			"fieldtype": "Link", "label": __("Cheque"),
		// 			"fieldname": "cheque",
		// 			"options": "Cheque",
		// 			"reqd": 1,
		// 			get_query: () => {
		// 				return {
		// 					query: "tech4all_pos_general.tech4all_pos_general.doctype.cheque.cheque.get_cheques",
		// 					filters: {
		// 						bank_account: frm.doc.bank_account,
		// 						status: "Available",
		// 						company: frm.doc.company
		// 					}
		// 				};
		// 			}
		// 		}
		// 	],
		// 	primary_action: function(){
		// 		frm.set_value("reference_no", cur_dialog.get_value("cheque"));
		// 		dialog.hide();
		// 		frm.set_df_property("reference_no", "read_only", 1);
		// 	}
		// });
		dialog.show();
	}
})