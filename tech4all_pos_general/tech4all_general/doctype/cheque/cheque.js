// Copyright (c) 2022, tech4all Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Cheque', {
	// refresh: function(frm) {

	// }
	status:function(frm) {
		if(frm.doc.status=="Issued")
		{
			frappe.throw(__("Cannot set cheque status to issued"))
		}
	}
});
