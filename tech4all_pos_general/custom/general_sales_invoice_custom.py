from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.party import get_party_details


def post_commission_jv(self, method):
	if self.total_commission and self.total_commission > 0:
		ss = frappe.get_doc("Selling Settings", "Selling Settings")
		if ss.get("enable_auto_commission_booking"):
			def get_company_account(company):
				for d in ss.commission_accounts:
					if company == d.company:
						return d.commission_expense_account
				return None
			commission_expense_account = get_company_account(self.company)
			supplier = frappe.db.get_value("Sales Partner", self.sales_partner, "supplier")
			if not supplier:
				return
			party_details = get_party_details(party=supplier, party_type="Supplier", company=self.company, doctype=self.doctype)

			if self.total_commission and not self.is_internal_transfer():
				jv = frappe.new_doc("Journal Entry")
				jv.company = self.company
				jv.posting_date = self.posting_date
				if jv.get("cost_center") is None:
					jv.cost_center = self.cost_center
				jv.voucher_type = 'Journal Entry'
				jv.user_remark = "Sales Commission against Sales Invoice: {0}".format(self.name)
				jv.sales_commission_invoice = self.name

				ac = jv.append("accounts", {})
				ac.account = party_details.credit_to
				ac.party_type = "Supplier"
				ac.party = supplier
				ac.credit_in_account_currency = self.total_commission
				ac.cost_center = self.cost_center

				bc = jv.append("accounts", {})
				bc.account = commission_expense_account
				bc.debit_in_account_currency = self.total_commission
				bc.cost_center = self.cost_center

				jv.insert()
				jv.submit()