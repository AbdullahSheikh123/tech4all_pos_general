frappe.ui.form.on("Cost Center Accounting",{
	onload_post_render: function(frm, cdt, cdn) {
		frm.trigger("cost_center_doctypes");
		let rows = cur_frm.get_field("cost_center_doctypes").grid.grid_rows;
		if (cur_frm.get_field("cost_center_doctypes").grid.grid_rows[0]) {	
			$.each(cur_frm.get_field("cost_center_doctypes").grid.grid_rows, (row) => {
				var row = rows[row];
				var childDoc = row.doc;
				var insert_after_value = childDoc.insert_after;
				add_options(frm, childDoc.doctype, childDoc.name);
				childDoc.insert_after = insert_after_value;
			});
			cur_frm.refresh_field('cost_center_doctypes');

		}
	},
	setup_default_views: (frm) => {
		frappe.model.set_default_views_for_doctype(frm.doc.name, frm);
	},
});

frappe.ui.form.on("Cost Center Doctypes", {
	document_type: function (frm, doctype, docname) {
		add_options(frm, doctype, docname);
	},

	fields_add: (frm) => {
		frm.trigger("setup_default_views");
	},
});


function add_options(frm, doctype, docname) {
	// console.log("add_options function invoked", doctype, docname);
    // Render two select fields for Fetch From instead of Small Text for better UX
	let grid = frm.get_field("cost_center_doctypes").grid;
	let docRow = grid.grid_rows_by_docname[docname];
	let field = docRow.columns.insert_after || '';
	let document_type = docRow.columns.document_type;
	let row = frappe.get_doc(doctype, docname);
	let curr_value = { fieldname: null };
	if (row.insert_after) {
		let [doctype, fieldname] = row.insert_after.split(".");
		curr_value.fieldname = fieldname;
		console.log("curr_value: ", curr_value);
	}

	row.insert_after = "";
	frm.dirty();
	update_fieldname_options();

	function update_fieldname_options() {
		field.find("option").remove();
		
		try {
			var _doctype = document_type.field.value;
		} 
		catch {
			let _rows = docRow.valueOf().grid.data;
			for (let i = 0; i < _rows.length; ++i) {
				if (_rows[i].name == docname){
					var _doctype = _rows[i].document_type;
				}
			}
		}
		if (_doctype) {
			frappe.model.with_doctype(_doctype, () => {
				let fields = frappe.meta
				  .get_docfields(_doctype, null, {
					fieldtype: ["not in", frappe.model.no_value_type],
				  })
				  .sort((a, b) => ( (a.label) ? a.label.localeCompare(b.label) : a.fieldname.localeCompare(b.fieldname) )) 
				  .map((df) => ({
					label: `${df.label} (${df.fieldtype})`,
					value: df.fieldname,
				  }));
				
				// Clear existing options
				field.find("option").remove();
				frappe.meta.get_docfield('Cost Center Doctypes', 'insert_after', docname).options = fields;
				// console.log(frappe.meta.get_docfield('Cost Center Doctypes', 'insert_after', docname));
				cur_frm.refresh_field('cost_center_doctypes');
			});
		}
	}
	
	field.on("change", () => {
		let insert_after = `${field.val()}`;
		row.insert_after = insert_after;
		frm.dirty();
	});

	if (curr_value.doctype) {
		document_type.val(curr_value.doctype);
		update_fieldname_options();
	}
}
