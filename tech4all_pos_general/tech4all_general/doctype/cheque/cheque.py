# Copyright (c) 2022, tech4all Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Cheque(Document):
	pass

@frappe.whitelist()
def get_cheques(doctype, txt, searchfield, start, page_len, filters):
	condition = ""
	if filters.get("bank_account"):
		condition += " and bank_account = %(bank_account)s"
	cheques = frappe.db.sql("""
		select name from `tabCheque`
		where
		status = 'Available'
		and company = %(company)s
		{condition}
		and name like %(txt)s
		limit %(start)s, %(page_len)s
		""".format(condition=condition),{
			"bank_account": filters.get("bank_account"),
			"company": filters.get("company"),
			'txt': "%%%s%%" % txt,
			'_txt': txt.replace("%", ""),
			'start': start,
			'page_len': page_len
		})
	return cheques
