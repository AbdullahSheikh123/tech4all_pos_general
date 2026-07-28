import frappe
from frappe import _
from frappe.custom.doctype.property_setter.property_setter import make_property_setter


def cost_center_validation(self, method):
    cost_center_settings = frappe.get_doc("Accounts Settings")
    
    if cost_center_settings.enable_cost_center_accounting:
        cost_center_doctypes = frappe.get_doc("Cost Center Accounting").cost_center_doctypes
        for cost_center_doctype in cost_center_doctypes:
            if self.doctype == cost_center_doctype.document_type:

                meta = frappe.get_meta(self.doctype)
                if cost_center_doctype.is_mandatory and meta.has_field('cost_center') and not self.cost_center:
                    frappe.throw(_("Cost Center field is mandatory"))
                if not meta.has_field("cost_center"):
                    frappe.throw(_("Cost Center Field does not exist!"))
                else:
                    if cost_center_settings.enforce_cost_center_in_child_tables:
                        if self.cost_center:
                            child_table_fields = meta.get_table_fields()
                            for child_table_field in child_table_fields:
                                child_table_doctype = child_table_field.options
                                child_table_meta = frappe.get_meta(child_table_doctype)
                                if child_table_meta.has_field("cost_center"):
                                    child_table_rows = getattr(self, child_table_field.fieldname)
                                    if child_table_rows:
                                        for row in child_table_rows:
                                            row.cost_center = self.cost_center
                break
