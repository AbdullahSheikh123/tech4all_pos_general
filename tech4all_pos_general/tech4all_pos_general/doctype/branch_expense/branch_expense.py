# Copyright (c) 2024, tech4allERP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class BranchExpense(Document):
    def on_submit(self):
        if not self.branch_cash_account:
            frappe.throw(_("Branch Cash Account is missing from POS profile"))

        if not self.expense_account:
            frappe.throw(_("Expense Account is missing from Branch Expense Template"))


        # if  self.total_amount<=0:
        #     frappe.throw(_("Total Amount should b greater then zero for debit and credit"))

        # Creating a new Journal Entry
        journal_entry = frappe.new_doc("Journal Entry")
        journal_entry.posting_date = frappe.utils.nowdate()
        journal_entry.company = self.company
        journal_entry.voucher_type = "Journal Entry"
        journal_entry.reference_doctype = "Branch Expense"
        journal_entry.custom_branch_expense = self.name
        journal_entry.reference_name = self.name

        journal_entry.append("accounts", {
            "account": self.expense_account,
            "debit_in_account_currency": self.total_amount,
            "credit_in_account_currency": 0,
            "cost_center": self.cost_center
        })

        journal_entry.append("accounts", {
            "account": self.branch_cash_account,
            "debit_in_account_currency": 0,
            "credit_in_account_currency": self.total_amount,
            "cost_center": self.cost_center
        })

        journal_entry.insert()
        journal_entry.submit()
