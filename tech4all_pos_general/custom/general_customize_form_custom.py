# Copyright (c) 2015, tech4allERP Pvt. Ltd. and Contributors
# License: MIT. See LICENSE
"""
	Utilities for using modules
"""
import json
import os

import frappe
import frappe.utils
from frappe import _
from frappe.utils import cint

def before_insert(self, method):
	if not frappe.get_conf().developer_mode:
		self.is_system_generated = 1


@frappe.whitelist()
def export_customizations(module, doctype, sync_on_migrate=0, with_permissions=0):
	"""Export Custom Field and Property Setter for the current document to the app folder.
	This will be synced with bench migrate"""

	sync_on_migrate = cint(sync_on_migrate)
	with_permissions = cint(with_permissions)

	if not frappe.get_conf().developer_mode:
		raise Exception("Not developer mode")

	custom = {
		"custom_fields": [],
		"property_setters": [],
		"custom_perms": [],
		"links": [],
		"doctype": doctype,
		"sync_on_migrate": sync_on_migrate,
	}

	def add(_doctype):
		custom["custom_fields"] += frappe.get_all("Custom Field", fields="*", filters={"dt": _doctype, "module": module})
		for d in custom["custom_fields"]:
			d.is_system_generated = 0
		custom["property_setters"] += frappe.get_all(
			"Property Setter", fields="*", filters={"doc_type": _doctype, "module": module}
		)
		for d in custom["property_setters"]:
			d.is_system_generated = 0
		custom["links"] += frappe.get_all("DocType Link", fields="*", filters={"parent": _doctype})

	add(doctype)

	if with_permissions:
		custom["custom_perms"] = frappe.get_all(
			"Custom DocPerm", fields="*", filters={"parent": doctype}
		)

	# also update the custom fields and property setters for all child tables
	for d in frappe.get_meta(doctype).get_table_fields():
		export_customizations(module, d.options, sync_on_migrate, with_permissions)

	if custom["custom_fields"] or custom["property_setters"] or custom["custom_perms"]:
		folder_path = os.path.join(frappe.get_module_path(module), "custom")
		if not os.path.exists(folder_path):
			os.makedirs(folder_path)

		path = os.path.join(folder_path, frappe.scrub(doctype) + ".json")
		with open(path, "w") as f:
			f.write(frappe.as_json(custom))

		frappe.msgprint(_("Customizations for <b>{0}</b> exported to:<br>{1}").format(doctype, path))
