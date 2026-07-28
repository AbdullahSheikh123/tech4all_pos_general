# Copyright (c) 2023, tech4all Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

class CostCenterAccounting(Document):
	def validate(self):
		document_types = []
		for index, item in enumerate(self.cost_center_doctypes):
			document_type = item.document_type

			if document_type not in document_types:
				document_types.append(document_type)
			else:
				frappe.throw(_("Duplicate <b>DocType</b> '{}' found at <b>Row '{}'</b>").format(document_type, (index+1)))

		self.validate_fields_in_cost_center_doctypes()
		self.verify_field_in_doctype()

	def validate_fields_in_cost_center_doctypes(self):
		for index, item in enumerate(self.cost_center_doctypes):
			if self.has_value_changed(item.document_type):
				docfields = [x.fieldname for x in frappe.get_meta(item.document_type).fields]
				for doccument_type in self.cost_center_doctypes:
					if doccument_type.insert_after not in docfields:
						frappe.throw(
							_("{0} is not a field of doctype {1}").format(
								frappe.bold(doccument_type.insert_after), frappe.bold(item.document_type)
							)
						)

	def verify_field_in_doctype(self):
		cost_center_settings = frappe.get_doc("Accounts Settings")
		if cost_center_settings.enable_cost_center_accounting:
			for row in self.cost_center_doctypes:
				document_type = row.document_type
				is_mandatory = row.is_mandatory
				insert_after = row.insert_after

				# print(f'DocType: {document_type}       Is_Mandatory: {is_mandatory}       Insert_After: {insert_after}')

				meta = frappe.get_meta(document_type)
				flag = False # Flag to check if the cost center field is present in the doctype
				flag0 = False
				for field in meta.fields:
					print(field.fieldname)
					if field.fieldname == 'cost_center':
						if is_mandatory and field.reqd:
							make_property_setter(document_type, field.fieldname, "reqd", 1, "Check")
						else:
							make_property_setter(document_type, field.fieldname, "reqd", 0, "Check")
						# print(f'Is Required: {field.reqd}')
						flag = True
					if field.fieldname == insert_after:
						flag0 = True
				
				# If inser_after field is not present then add cost center field
				if not flag0:
					frappe.throw(
							_("{0} is not a field of doctype {1}<br>Kindly provide correct Insert After <b>fieldname</b>").format(
								frappe.bold(insert_after), frappe.bold(document_type)
							)
						)
					break
				# If cost center field is not present then add cost center field
				elif not flag:
					frappe.get_doc(
						{
							"is_system_generated": 1,
							"dt": document_type,
							"label": "Cost Center",
							"fieldname": "cost_center",
							"insert_after": insert_after,
							"fieldtype": "Link",
							"options": "Cost Center",
							"reqd": is_mandatory,
							"doctype": "Custom Field",
						}
					).save()
					frappe.db.commit()
					break


@frappe.whitelist()
def get_options(doctype):
	meta = frappe.get_meta(doctype)
	options = []
	for field in meta.fields:
		options.append({"value": field.fieldname, "label": field.label, "type": field.fieldtype})
	return options
