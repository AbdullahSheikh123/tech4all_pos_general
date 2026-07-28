frappe.ui.form.on("User permission Setting", {
    refresh: function (frm) {
        update_all_rows(frm); // Ensure all rows are updated on refresh
    }
});

// Correcting event binding to the child table
frappe.ui.form.on("User permission Setting Doctypes", {
    doctypelink: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row && row.doctypelink) {
            update_field_options(frm, row.doctypelink, cdt, cdn);
        }
    }
});

function update_all_rows(frm) {
    let table_fieldname = "doctypes";
    
    setTimeout(() => {
        (frm.doc[table_fieldname] || []).forEach(row => {
            if (row.doctypelink) {
                update_field_options(frm, row.doctypelink, row.doctype, row.name);
            }
        });
    }, 500);
}

function update_field_options(frm, selected_doctype, cdt, cdn) {
    if (!selected_doctype) return;

    frappe.model.with_doctype(selected_doctype, function () {
        let meta = frappe.get_meta(selected_doctype);
        let field_options = meta.fields.map(f => f.fieldname).join("\n");

        let table_fieldname = "doctypes";
        frm.fields_dict[table_fieldname].grid.update_docfield_property(
            "filter_apply_on",
            "options",
            field_options
        );
    });
}
