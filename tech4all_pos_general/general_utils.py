from __future__ import unicode_literals
import frappe
from frappe import _
import json
from frappe.utils import cint, flt
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.model.workflow import get_workflow

def before_naming(self, method):
	if self.get("company"):
		self.abbr = frappe.db.get_value("Company", self.get("company"), "abbr")

def sync_customizations_for_doctype(data, folder, filename: str = ""):
	"""Sync doctype customzations for a particular data set"""
	from frappe.core.doctype.doctype.doctype import validate_fields_for_doctype

	doctype = data["doctype"]
	update_schema = False

	def sync(key, custom_doctype, doctype_fieldname):
		doctypes = list(set(map(lambda row: row.get(doctype_fieldname), data[key])))

		# sync single doctype exculding the child doctype
		def sync_single_doctype(doc_type):
			def _insert(data):
				if data.get(doctype_fieldname) == doc_type:
					data["doctype"] = custom_doctype
					doc = frappe.get_doc(data)
					doc.db_insert()

			if custom_doctype != "Custom Field":
				if not custom_doctype == "Property Setter":
					return
				if "module" in data and data["module"]:
					frappe.db.delete(custom_doctype, {doctype_fieldname: doc_type, "module": data["module"], "is_system_generated": 0})


				for d in data[key]:
					d["doctype"] = custom_doctype
					doc = frappe.get_doc(d)
					if not doc.name:
						doc.autoname()
						
					if not frappe.db.exists(custom_doctype, doc.name):
						_insert(d)

			else:
				for d in data[key]:
					field = frappe.db.get_value("Custom Field", {"dt": doc_type, "fieldname": d["fieldname"]})
					if not field:
						d["owner"] = "Administrator"
						_insert(d)
					else:
						custom_field = frappe.get_doc("Custom Field", field)
						custom_field.flags.ignore_validate = True
						custom_field.update(d)
						custom_field.db_update()

		for doc_type in doctypes:
			# only sync the parent doctype and child doctype if there isn't any other child table json file
			if doc_type == doctype or not os.path.exists(
				os.path.join(folder, frappe.scrub(doc_type) + ".json")
			):
				sync_single_doctype(doc_type)

	if not frappe.db.exists("DocType", doctype):
		print(_("DocType {0} does not exist.").format(doctype))
		print(_("Skipping fixture syncing for doctyoe {0} from file {1} ").format(doctype, filename))
		return

	if data["custom_fields"]:
		sync("custom_fields", "Custom Field", "dt")
		update_schema = True

	if data["property_setters"]:
		sync("property_setters", "Property Setter", "doc_type")

	if data.get("custom_perms"):
		sync("custom_perms", "Custom DocPerm", "parent")

	print(f"Updating customizations for {doctype}")
	validate_fields_for_doctype(doctype)

	if update_schema and not frappe.db.get_value("DocType", doctype, "issingle"):
		frappe.db.updatedb(doctype)

@frappe.whitelist()
def get_open_activities(ref_doctype, ref_docname):
	tasks = get_open_todos(ref_doctype, ref_docname)
	events = get_open_events(ref_doctype, ref_docname)

	return {"tasks": tasks, "events": events}


def get_open_todos(ref_doctype, ref_docname):
	return frappe.get_all(
		"ToDo",
		filters={"reference_type": ref_doctype, "reference_name": ref_docname, "status": "Open"},
		fields=[
			"name",
			"description",
			"allocated_to",
			"date",
		],
	)


def get_open_events(ref_doctype, ref_docname):
	event = frappe.qb.DocType("Event")
	event_link = frappe.qb.DocType("Event Participants")

	query = (
		frappe.qb.from_(event)
		.join(event_link)
		.on(event_link.parent == event.name)
		.select(
			event.name,
			event.subject,
			event.event_category,
			event.starts_on,
			event.ends_on,
			event.description,
		)
		.where(
			(event_link.reference_doctype == ref_doctype)
			& (event_link.reference_docname == ref_docname)
			& (event.status == "Open")
		)
	)
	data = query.run(as_dict=True)

	return data


def get_itemised_tax(taxes, with_tax_account=False):
	itemised_tax = {}
	for tax in taxes:
		if getattr(tax, "category", None) and tax.category == "Valuation":
			continue

		item_tax_map = json.loads(tax.item_wise_tax_detail) if tax.item_wise_tax_detail else {}
		if item_tax_map:
			for item_code, tax_data in item_tax_map.items():
				itemised_tax.setdefault(item_code, frappe._dict({"total": 0, "breakup": frappe._dict()}))

				tax_rate = 0.0
				tax_amount = 0.0

				if isinstance(tax_data, list):
					tax_rate = flt(tax_data[0])
					tax_amount = flt(tax_data[1])
				else:
					tax_rate = flt(tax_data)

				itemised_tax[item_code]["total"] += tax_amount
				itemised_tax[item_code]["breakup"][tax.description] = frappe._dict(
					dict(tax_rate=tax_rate, tax_amount=tax_amount)
				)

				if with_tax_account:
					itemised_tax[item_code]["breakup"][tax.description].tax_account = tax.account_head

	return itemised_tax


@frappe.whitelist()
def get_address_and_contact(doctype, docname):
	doc = frappe.get_doc(doctype, docname)
	load_address_and_contact(doc)
	return frappe._dict({"address": doc.__onload.addr_list, "contact": doc.__onload.contact_list})


@frappe.whitelist()
def get_all_roles(arg=None):
	"""return all roles"""
	active_domains = frappe.get_active_domains()
	filters = {"name": ("not in", "Administrator,Guest,All"), "disabled": 0}

	if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
		pass
	else:
		filters["name"] = ["in", frappe.get_roles()]

	roles = frappe.get_all(
		"Role",
		filters=filters,
		or_filters={"ifnull(restrict_to_domain, '')": "", "restrict_to_domain": ("in", active_domains)},
		order_by="name",
	)

	return [role.get("name") for role in roles]


def onload_user(self, method):
	try:
		# Frappe v16+
		from frappe.utils.modules import get_modules_from_all_apps
	except ImportError:
		# Frappe v15
		from frappe.config import get_modules_from_all_apps

	all_modules = [m.get("module_name") for m in get_modules_from_all_apps()]

	if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles():
		pass
	else:
		all_modules = []
		blocked_module = [d.module for d in frappe.get_doc("User", frappe.session.user).block_modules]

		for m in get_modules_from_all_apps():
			if m.get("module_name") not in blocked_module:
				all_modules.append(m.get("module_name"))
				
	all_modules = sorted(all_modules)

	self.set_onload("all_modules", all_modules)



def get_doc_workflow(self, method):
	print(123213)
	workflow = get_workflow(self)
	print(workflow)
	if workflow:
		self.get("__onload").workflow_doc = workflow.as_dict()
