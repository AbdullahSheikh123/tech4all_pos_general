frappe.ui.form.Form.prototype.refresh = function(docname) {
    var switched = docname ? true : false;

    removeEventListener("beforeunload", this.beforeUnloadListener, { capture: true });

    if (docname) {
        this.switch_doc(docname);
    }

    cur_frm = this;

    // Register a custom onload_post_render event handler for the current form's doctype
    frappe.ui.form.on(cur_frm.doctype, {
        onload_post_render: function(frm) {
            // Get the doctype from the current form
            doctype = frm.doctype;
            frappe.call({
                method: "tech4all_pos_general.tech4all_general.doctype.document_defaults.document_defaults.check_document_defaults",
                args: {
                    doctype: frm.doctype
                },
                callback: function(r) {
                    if (r) {
                        if (r.message == true) {
                            // Apply document defaults to the form
                            applyDocumentDefaults(frm, doctype);
                            
                            // Process child tables in the form
                            processChildTables(frm);
                        }
                    }
                }
            });
        },
    });
  
    if (cur_frm) {
        // Get the document fields for the current form's doctype
        var docfields = frappe.meta.get_docfields(cur_frm.doctype);
      
        // Iterate over each document field
        for (var k = 0; k < docfields.length; k++) {
          var df = docfields[k];
      
          // Check if the field is of type "Table"
          if (df.fieldtype == "Table") {
            const doctype = df.options;
      
            // Register a custom onload event handler for the child table doctype
            frappe.ui.form.on(doctype, {
              onload: function(frm, cdt, cdn) {
                // Trigger the specific add event for the child table field
                frm.trigger([`${df.fieldname}_add`]);
              },
              [`${df.fieldname}_add`]: function(frm, cdt, cdn) {
                // Get the child document from the locals dictionary
                const child = locals[cdt][cdn];
      
                // Apply document defaults to the child table
                applyDocumentDefaults(frm, doctype, child);
              },
            });
          }
        }
    }  

    this.undo_manager.erase_history();

    if (this.docname) {
        // document to show
        this.save_disabled = false;
        // set the doc
        this.doc = frappe.get_doc(this.doctype, this.docname);

        // check permissions
        this.fetch_permissions();
        if (!this.has_read_permission()) {
            frappe.show_not_permitted(__(this.doctype) + " " + __(cstr(this.docname)));
            return;
        }

        // update grids with new permissions
        this.grids.forEach((table) => {
            table.grid.refresh();
        });

        // read only (workflow)
        this.read_only = frappe.workflow.is_read_only(this.doctype, this.docname);
        if (this.read_only) {
            this.set_read_only(true);
            frappe.show_alert(__("This form is not editable due to a Workflow."));
        }

        // check if doctype is already open
        if (!this.opendocs[this.docname]) {
            this.check_doctype_conflict(this.docname);
        } else {
            if (this.check_reload()) {
                return;
            }
        }

        // do setup
        if (!this.setup_done) {
            this.setup();
        }

        // load the record for the first time, if not loaded (call 'onload')
        this.trigger_onload(switched);

        // if print format is shown, refresh the format
        // if(this.print_preview.wrapper.is(":visible")) {
        //  this.print_preview.preview();
        // }

        if (switched) {
            if (this.show_print_first && this.doc.docstatus === 1) {
                // show print view
                this.print_doc();
            }
        }

        // set status classes
        this.$wrapper
            .removeClass("validated-form")
            .toggleClass("editable-form", this.doc.docstatus === 0)
            .toggleClass("submitted-form", this.doc.docstatus === 1)
            .toggleClass("cancelled-form", this.doc.docstatus === 2);

        this.show_conflict_message();

        if (frappe.boot.read_only) {
            this.disable_form();
        }
    }
}

// Apply document defaults to child tables
function processChildTables(frm) {
    // Get the document fields for the current form's doctype
    var docfields = frappe.meta.get_docfields(frm.doctype);
  
    // Iterate over each document field
    for (var k = 0; k < docfields.length; k++) {
      var df = docfields[k];
      
      // Check if the field is of type "Table"
      if (df.fieldtype == "Table") {
        const doctype = df.options;
        
        // Get the child table field from the form
        var childTable = cur_frm.fields_dict[df.fieldname];
        
        // Check if the child table field exists and has a grid
        if (childTable && childTable.grid) {
          var rows = childTable.grid.grid_rows;
          
          // Iterate over each row in the child table
          for (var i = 0; i < rows.length; i++) {
            var row = rows[i];
            var child = locals[row.doc.doctype][row.doc.name];
            
            // Apply document defaults to the document
            applyDocumentDefaults(frm, doctype, child);
          }
        }
      }
    }
}


function applyDocumentDefaults(frm, doctype, child=false) {
    if (cur_frm.is_new()) {
        document_defaults = frappe.boot.document_defaults;
        
        if (document_defaults) {
        
            // Create a map to store field-value pairs for each condition
            var fieldValuesMap = {};
        
            // Separate user-specific defaults and generic defaults
            var userSpecificDefaults = [];
            var genericDefaults = [];
        
            // Iterate over the document defaults and populate the userSpecificDefaults and genericDefaults arrays
            if (child) {
                for (var i = 0; i < document_defaults.length; ++i) {
                    var defaultData = document_defaults[i];
                    if (defaultData.document_type === cur_frm.doctype) {
                        if (defaultData.user === frappe.session.user) {
                            userSpecificDefaults.push(defaultData);
                        } else {
                            genericDefaults.push(defaultData);
                        }
                    }
                }
            } else {
                for (var i = 0; i < document_defaults.length; ++i) {
                    var defaultData = document_defaults[i];
                    if (defaultData.document_type === doctype) {
                        if (defaultData.user === frappe.session.user) {
                            userSpecificDefaults.push(defaultData);
                        } else {
                            genericDefaults.push(defaultData);
                        }
                    }
                }
            }

            // Determine which defaults to apply
            var defaultsToApply = userSpecificDefaults.length > 0 ? userSpecificDefaults : genericDefaults;

            // Iterate over the selected defaults and populate the fieldValuesMap
            for (var i = 0; i < defaultsToApply.length; ++i) {
                var conditions = defaultsToApply[i].conditions;
                for (var j = 0; j < conditions.length; ++j) {
                    var condition = conditions[j];
                    fieldValuesMap[condition.field] = condition.value_for;
                }
            }

            // Apply the field values to the form fields
            frappe.model.with_doctype(doctype, () => {
                var docfields = frappe.meta.get_docfields(doctype);
                for (var k = 0; k < docfields.length; k++) {
                    var df = docfields[k];
                    
                    if (fieldValuesMap.hasOwnProperty(df.fieldname)) {
                        if (child) {
                            var child_locals = locals[child.doctype];
                            $.each(child_locals, function (i, v) {
                                v[df.fieldname] = fieldValuesMap[df.fieldname];
                            });
                            frappe.meta.docfield_map[child.doctype][df.fieldname].default = fieldValuesMap[df.fieldname];
                        } else {
                            frm_field = cur_frm.fields_dict[df.fieldname];
                            frm_field.set_value(fieldValuesMap[df.fieldname]);
                        }
                    }
                }
                if (cur_frm && cur_frm.fields_dict[df.fieldname]) {
                    var grid = cur_frm.fields_dict[df.fieldname].grid;
                    if (grid) {
                        // Trigger ${df.fieldname}_add event for existing child table rows
                        grid.grid_rows.forEach(function(row) {
                            var childDoc = row.doc;
                            frappe.ui.form.trigger(childDoc.doctype, `${df.fieldname}_add`, [frm, childDoc.doctype, childDoc.name]);
                        });
                    }
                }
            });
            
        }
    }
}
