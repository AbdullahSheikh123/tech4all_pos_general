from __future__ import unicode_literals
import frappe
from frappe import _


def on_validate(self, method):
    if self.accounts:
        field_map = {"Supplier": "supplier_name", "Customer": "customer_name", "Employee": "employee_name", "Shareholder": "title"}
        for entry in self.accounts:
            if entry.party_type:
                print(frappe.db.get_value(entry.party_type, {"name": entry.party}, field_map[entry.party_type]))
                entry.party_name = frappe.db.get_value(entry.party_type, {"name": entry.party}, field_map[entry.party_type]) or ''


def on_submit(self,method):
    if self.cheque_no:
         if frappe.db.exists("Cheque",self.cheque_no):
            cheque = frappe.get_doc("Cheque",self.cheque_no)
            for entry in self.accounts:
                if entry.credit>0 and cheque.bank_account==entry.bank_account:
                    frappe.db.set_value("Cheque",self.cheque_no,{"status": "Issued", "reference_doctype": self.doctype, "reference_name":self.name})
                    break
            

def on_cancel(self,method):

    if self.cheque_no:
        if frappe.db.exists("Cheque",self.cheque_no):
            frappe.db.set_value("Cheque",self.cheque_no,{"status": "Available", "reference_doctype": "", "reference_name": ""})
