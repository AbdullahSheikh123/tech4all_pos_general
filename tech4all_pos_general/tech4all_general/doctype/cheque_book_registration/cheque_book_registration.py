# Copyright (c) 2022, tech4all Tech and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class ChequeBookRegistration(Document):
	pass

@frappe.whitelist()
def create_cheque(chequebook,series_from,number_of_leafs,bank_account,company,bank_name,dt,dn):
	
	for x in range(0,int(number_of_leafs)):
		cheque = frappe.new_doc("Cheque")
		cheque.cheque_book = chequebook
		cheque.company = company
		cheque.bank_account = bank_account
		cheque.bank_name = bank_name
		cheque.cheque_number = series_from
		if not x == 0:
			lastnode = series_from
			cheque.cheque_number = str(int(lastnode) + x)
			if len(series_from) > 4:
				lastnode = series_from[-5:]
				cheque.cheque_number = series_from[:-5] + '{0}'.format(lastnode[0] if lastnode[0] == '0' else '') +str(int(lastnode)+x)
		cheque.status = 'Available'
		cheque.name = cheque.cheque_number
		cheque.save(ignore_permissions=True)
		frappe.db.set_value(dt,dn,"cheques_created",1)

	return ""
		

