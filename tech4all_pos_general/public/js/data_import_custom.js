// Copyright (c) 2019, tech4allerp and contributors
// For license information, please see license.txt

frappe.ui.form.on("Data Import", {
	download_template(frm) {
		frappe.require("data_import_tools.bundle.js", () => {
            frappe.data_import.DataExporter.prototype.select_mandatory = function select_mandatory() {
                this.unselect_all();
                this.dialog.$wrapper.find(".label-area.text-danger").siblings("input[type='checkbox']").prop("checked", true).trigger("change");
            }
		});
	},
});