from __future__ import unicode_literals

import frappe
from frappe import _
from erpnext.accounts.doctype.payment_entry.payment_entry import get_outstanding_reference_documents




def before_submit(self,method):
    self.validate_allocated_amount()
    if self.docstatus ==1 and self.payment_type =="Pay" and self.mode_of_payment == "Cheque":
        if frappe.db.exists("Cheque",self.reference_no):
            cheque=frappe.get_doc("Cheque",self.reference_no)
            if cheque.status != "Available":
                frappe.throw(_("Attached Cheque is already used in "+cheque.reference_doctype+" "+cheque.reference_name))
            frappe.db.set_value("Cheque",self.reference_no,{"status": "Issued", "reference_doctype": self.doctype, "reference_name":self.name})

def on_cancel(self,method):

    if self.docstatus ==2 and self.payment_type =="Pay" and self.mode_of_payment == "Cheque":
        if frappe.db.exists("Cheque",self.reference_no):
            frappe.db.set_value("Cheque",self.reference_no,{"status": "Available", "reference_doctype": "", "reference_name": ""})


@frappe.whitelist()
def get_outstanding_reference_documents_override(args):

    outstandings = get_outstanding_reference_documents(args)
    non_return = []
    for outstanding in outstandings:
        if outstanding.voucher_type in ["Sales Invoice","Purchase Invoice"]:
            voucher = frappe.get_doc(outstanding.voucher_type,outstanding.voucher_no)
            if not voucher.is_return:  
                non_return.append(outstanding)
        else:
            non_return.append(outstanding)
    return non_return