// Copyright (c) 2023, tech4all Tech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Default View', {
	refresh: function(frm) {
		if(frm.doc.document_type){
			frm.trigger("document_type");
		}
	},
	document_type: function(frm){
		if(frm.doc.document_type){
			frappe.run_serially([
				() => frappe.model.with_doctype(frm.doc.document_type, () => {
						frm.document_type_meta = frappe.get_meta(frm.doc.document_type);
					}),
				() => frm.trigger("set_docfield_options")
			]);
		}
	},
	set_docfield_options: function(frm){
		var $input = frm.get_field("docfield").$input;
		var input = $input.get(0);
		var data = [];
		$.each(frm.document_type_meta.fields, function(i,v){
			if(["Select", "Link", "Check"].includes(v.fieldtype)){
				data.push({"value": v.fieldname, "label": v.label});
			}
		});

		var awesomplete = new Awesomplete(input, {
			minChars: 0,
			maxItems: 99,
			autoFirst: false,
			list: data,
			filter: function (text, term) {
				return true;
			},
			data: function (item, input) {
				return {
					label: item.label || item.value,
					value: item.value,
				};
			},
			sort: function (a, b) {
				return b.label - a.label;
			},
		});
		$input.on(
			"input",
			frappe.utils.debounce(function (e) {
				var value = e.target.value;
				var txt = value.trim().replace(/\s\s+/g, " ");
				var last_space = txt.lastIndexOf(" ");
				var options = [];
				$.each(data, function(i,v){
					var search = frappe.search.utils.fuzzy_search(txt, v.label);
					if (search){
						options.push(data[i]);
					}
				});
				awesomplete.list = options;
				if(options.length == 0){
					item_selected = false;
				}
			}, 100)
		);
		var autocomplete_open = false;
		var item_selected = false;
		if($input.val()){
			item_selected = true;
		}

		$input.on('focus', function(e) {
			$(e.target).trigger('input');
		});

		$input.on('focusout', function(e) {
			if(!item_selected && $input.val()){
				$input.val("");
			}
			else if(item_selected && $input.val()){
				frm.trigger("load_docfield_value");
			}
		});

		$input.on("awesomplete-open", function (e) {
			autocomplete_open = e.target;
		});

		$input.on("awesomplete-close", function (e) {
			autocomplete_open = false;
		});

		$input.on("awesomplete-select", function (e) {
			var o = e.originalEvent;
			var value = o.text.value;
			var item = awesomplete.get_item(value);
			item_selected = true;
		});

	},
	load_docfield_value: function(frm){
		
	}

});
