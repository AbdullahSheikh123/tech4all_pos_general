frappe.ui.form.on('Journal Entry', {
	onload_post_render: function(frm){
		
		if(frm.doc.docstatus == 0 ){
            console.log("check")
            frm.add_custom_button("Attach Cheque", function(){
				frm.trigger("select_cheque");
			}).addClass('btn btn-primary');
			
		}
	},
    select_cheque: function(frm){
		
		

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
								
								status: "Available",
								company: frm.doc.company
							}
						};
					}
				}
			],
			primary_action: function(){
				frm.set_value("cheque_no", cur_dialog.get_value("cheque"));
				
				dialog.hide();
			}
		});
		dialog.show();
	}
})