# Copyright (c) 2023, tech4all Tech and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class PriceListSetting(Document):

	def validate(self):
		fields = []
		for index, item in enumerate(self.item_price_table):
			field = item.item_code

			if field not in fields:
				fields.append(field)
			else:
				frappe.throw(_("Duplicate <b>Entry</b> '{}' found at <b>Row '{}'</b>").format(field, (index+1)))

		rows = self.item_price_table
		item_price_list = frappe.get_list("Item Price", fields=["item_code", "name"])

		item_code_to_name = {item.item_code: item.name for item in item_price_list}

		# Create sets for easy comparison
		existing_items = set(list(item_code_to_name.keys()))
		current_items = set([row.item_code for row in rows])

		# Insert new rows
		for row in rows:
			if row.item_code not in existing_items:
				frappe.get_doc({
					"doctype": "Item Price",
					"item_code": row.item_code,
					"item_name": row.item_name,
					"uom": row.uom,
					"packing_unit": row.packing_unit,
					"brand": row.brand,
					"item_description": row.item_description,
					"price_list": row.price_list,
					"customer": row.customer,
					"supplier": row.supplier,
					"batch_no": row.batch_no,
					"buying": row.buying,
					"selling": row.selling,
					"currency": row.currency,
					"price_list_rate": row.price_list_rate,
					"valid_from": row.valid_from,
					"lead_time_days": row.lead_time_days,
					"valid_upto": row.valid_upto,
					"note": row.note,
					"reference": row.reference,
				}).insert()

		# Update existing rows
		for row in rows:
			if row.item_code in existing_items:
				name = item_code_to_name[f'{row.item_code}']
				doc = frappe.get_doc("Item Price", name)
				doc.item_code = row.item_code
				doc.item_name = row.item_name
				doc.uom = row.uom
				doc.packing_unit = row.packing_unit
				doc.brand = row.brand
				doc.item_description = row.item_description
				doc.price_list = row.price_list
				doc.customer = row.customer
				doc.supplier = row.supplier
				doc.batch_no = row.batch_no
				doc.buying = row.buying
				doc.selling = row.selling
				doc.currency = row.currency
				doc.price_list_rate = row.price_list_rate
				doc.valid_from = row.valid_from
				doc.lead_time_days = row.lead_time_days
				doc.valid_upto = row.valid_upto
				doc.note = row.note
				doc.reference = row.reference
				doc.save()

		# Remove deleted rows
		removed_items = existing_items - current_items
		for item_code in removed_items:
			name = item_code_to_name[f'{item_code}']
			frappe.delete_doc("Item Price", name)

	def onload(self):
		"""
			Loads the item prices in the table
		"""
		item_codes = [row.item_code for row in self.item_price_table]

		item_prices = frappe.get_list("Item Price", fields=["*"])
		for item_price in item_prices:
			if item_price.item_code not in item_codes:
				self.append("item_price_table", item_price)


@frappe.whitelist()
def update_price_list_rate(price_list, rate):
	items = frappe.get_list("Item Price", filters={"price_list": price_list}, fields=["name"])

	for item in items:
		item_doc = frappe.get_doc("Item Price", item.name)
		item_doc.set("price_list_rate", rate)
		item_doc.save()
	
	doc = frappe.get_doc("Price List Setting")
	for row in doc.item_price_table:
		if row.price_list == price_list:
			row.price_list_rate = rate

	doc.save()
