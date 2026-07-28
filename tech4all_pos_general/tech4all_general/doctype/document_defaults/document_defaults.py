import frappe
from frappe import _
from frappe.model.document import Document

class DocumentDefaults(Document):
	def validate(self):

		filters = {"company": self.company, "document_type":self.document_type, "name": ["!=", self.name]}
		exception_message = "Defaults of document {0} already exist for company {1}"

		if self.user:
			filters.update({"user": self.user})
			exception_message += " and for user {2}"

		existing_records = frappe.db.get_list("Document Defaults", filters=filters)

		if existing_records:
			frappe.throw(
				_(exception_message).format(
					frappe.bold(self.document_type), frappe.bold(self.company), frappe.bold(self.user)
				)
			)
		fields = []
		for index, item in enumerate(self.conditions):
			field = item.field
			
			if field not in fields:
				fields.append(field)
			else:
				frappe.throw(_("Duplicate <b>Field</b> '{}' found at <b>Row '{}'</b>").format(field, (index+1)))

		self.validate_fields_in_conditions()

	def validate_fields_in_conditions(self):
		if self.has_value_changed("document_type"):
			docfields = [x.fieldname for x in frappe.get_meta(self.document_type).fields]
			for condition in self.conditions:
				if condition.field not in docfields:
					frappe.throw(
						_("{0} is not a field of doctype {1}").format(
							frappe.bold(condition.field), frappe.bold(self.document_type)
						)
					)
				else:
					field = frappe.get_meta(self.document_type).get_field(condition.field)
					value = condition.value_for

					if field.fieldtype == "Select":
						options = field.options
						if value not in options:
							frappe.throw(
								_("{0} field has no option {1}").format(
									frappe.bold(field.label), frappe.bold(value)
								)
							)
					elif field.fieldtype == "Check":
						if str(value) not in '0 1':
							frappe.throw(
								_("Invalid value {1}. Field {0} only accepts values \'0\' or \'1\'").format(
									frappe.bold(field.label), frappe.bold(value)
								)
							)
					elif field.fieldtype == "Link":
							if not frappe.db.exists(field.options, value):
								frappe.throw(
									_("{0} not found in {1}").format(
										frappe.bold(value), frappe.bold(field.options) 
									)
								)


@frappe.whitelist()
def get_options(field, fieldtype='', name='', options='', label=''):
	if fieldtype == "Select":
		options = options.split('\n')
	elif fieldtype == "Check":
		options = [{"label": "Yes", "value": "1"}, {"label": "No", "value": "0"}]
	elif fieldtype == "Link":
		options = frappe.db.get_list(options, pluck='name')
	return options


@frappe.whitelist()
def get_document_defaults(doctype):

    # Fetch the conditions from the "Document Defaults" doctype and its child table "Document Defaults Condition"
	if doctype == "Document Defaults":
		return
	document_defaults = frappe.get_doc("Document Defaults", {"document_type": doctype})

	if document_defaults: return document_defaults

@frappe.whitelist()
def check_document_defaults(doctype):
	docs = frappe.get_list("Document Defaults", filters={"document_type": doctype})
	if docs:
		return True
	else:
		return False
