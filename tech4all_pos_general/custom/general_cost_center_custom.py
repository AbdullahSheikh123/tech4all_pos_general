import frappe
from frappe import _
from frappe.utils import cint


def cost_center_validation(doc, method=None):
    """Apply cost-center rules without blocking installs or migrations.

    This is a wildcard doc_event, so Frappe also calls it while syncing
    DocTypes, customizations, and fixtures. Custom fields may not exist yet
    during those operations.
    """
    settings_meta = frappe.get_meta("Accounts Settings")
    if not settings_meta.has_field("enable_cost_center_accounting"):
        return

    cost_center_settings = frappe.get_doc("Accounts Settings")
    if not cint(getattr(cost_center_settings, "enable_cost_center_accounting", 0)):
        return

    if not frappe.db.exists("DocType", "Cost Center Accounting"):
        return

    cost_center_doctypes = getattr(
        frappe.get_doc("Cost Center Accounting"), "cost_center_doctypes", []
    )
    for cost_center_doctype in cost_center_doctypes:
        if doc.doctype != cost_center_doctype.document_type:
            continue

        meta = frappe.get_meta(doc.doctype)
        if not meta.has_field("cost_center"):
            frappe.throw(_("Cost Center Field does not exist!"))

        if cost_center_doctype.is_mandatory and not getattr(doc, "cost_center", None):
            frappe.throw(_("Cost Center field is mandatory"))

        if (
            cint(getattr(cost_center_settings, "enforce_cost_center_in_child_tables", 0))
            and getattr(doc, "cost_center", None)
        ):
            for child_table_field in meta.get_table_fields():
                child_table_meta = frappe.get_meta(child_table_field.options)
                if not child_table_meta.has_field("cost_center"):
                    continue

                for row in getattr(doc, child_table_field.fieldname, []) or []:
                    row.cost_center = doc.cost_center
        break
