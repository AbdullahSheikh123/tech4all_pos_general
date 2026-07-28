frappe.provide("frappe.search");

frappe.ui.form.on("Document Defaults", {
	refresh: function (frm, cdt, cdn) {
		frm.trigger("document_type");
        const child = locals[cdt][cdn];
        if(frm.doc.document_type) {
            frappe.model.with_doctype(frm.doc.document_type, () => {
                const meta = frappe.get_meta(frm.doc.document_type);
                frm.option_fields = {};
                let fieldnames = [];
                $.each(meta.fields || [], function(i,v){
                fieldnames.push({label: v.label, value: v.fieldname});
                    frm.option_fields[v.fieldname] = v;
                });
                var rows = cur_frm.fields_dict["conditions"].grid.grid_rows;
                for (var i=0; i < rows.length; ++i) {
                    add_options(frm, i, child);
                }
            });
        }
	},
	document_type: (frm) => {
		// Update the select field options with fieldnames
		if (frm.doc.document_type) {
			// Check if the selected doctype has a field named "company"
			frappe.model.with_doctype(frm.doc.document_type, () => {
				const meta = frappe.get_meta(frm.doc.document_type);
				const companyField = meta.fields.find((field) => field.fieldname === 'company');
				if (companyField) {
					frm.set_df_property('company', 'reqd', 1); // Make the 'company' field mandatory
				} else {
					frm.set_df_property('company', 'reqd', 0); // Make the 'company' field optional
				}

                let fieldnames = [];
                frm.option_fields = {};
                $.each(meta.fields || [], function(i,v){
                    if(['Select', 'Check', 'Link'].includes(v.fieldtype)){
                        fieldnames.push({label: v.label, value: v.fieldname});
                        frm.option_fields[v.fieldname] = v;
                    }
                });
                frm.fields_dict.conditions.grid.update_docfield_property(
                    "field",
                    "options",
                    fieldnames
                );
			});
		}
	},
});


frappe.ui.form.on('Document Defaults Condition', {
    field: function(frm, cdt, cdn) {
        frm.refresh_field('value_for');
        const child = locals[cdt][cdn];
        const fd = frm.option_fields[child.field];
        var val = cur_frm.fields_dict["conditions"].grid.grid_rows[child.idx-1].columns.value_for;

        if(val.df.fieldtype !== 'Select') {
            return
        }
        
        frappe.call({
            method: "tech4all_pos_general.tech4all_pos_general.doctype.document_defaults.document_defaults.get_options",
            args: {
                field: fd,
                // attribute_value: term,
                fieldtype: fd.fieldtype,
                name: fd.fieldname,
                options: fd.options,
                label: fd.label
            },
            callback: function(r) {
                if (r.message) {
                    val.df.options = r.message;
                    val.last_options = r.message;

                    frm.refresh_field("conditions");
                }
            }
        });
    },
});


function add_options(frm, row, child) {
    var fd = frm.option_fields[cur_frm.fields_dict["conditions"].doc.conditions[row].field];
    var val = cur_frm.fields_dict["conditions"].grid.grid_rows[row].columns.value_for;
    frappe.call({
        method: "tech4all_pos_general.tech4all_pos_general.doctype.document_defaults.document_defaults.get_options",
        args: {
            field: fd,
            fieldtype: fd.fieldtype,
            name: fd.fieldname,
            options: fd.options,
            label: fd.label
        },
        callback: function(r) {
            if (r.message) {
                val.df.options = r.message;
                val.last_options = r.message;
                frm.refresh_field("conditions");
            }
        }
    });
}
