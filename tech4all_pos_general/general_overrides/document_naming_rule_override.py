import frappe
from frappe.core.doctype.document_naming_rule.document_naming_rule import DocumentNamingRule
from frappe.utils.data import evaluate_filters
from frappe.model.naming import parse_naming_series


class DocumentNamingRuleOverride(DocumentNamingRule):
    def __init__(self, *args, **kwargs):
        super(DocumentNamingRule, self).__init__(*args, **kwargs)

    def validate_fields_in_conditions(self):
        if self.has_value_changed("document_type"):
            docfields = [x.fieldname for x in frappe.get_meta(self.document_type).fields]
            for condition in self.conditions:
                if condition.field not in docfields and condition.field != "owner":
                    frappe.throw(("{0} is not a field of doctype {1}").format(frappe.bold(condition.field), frappe.bold(self.document_type)))

    def apply(self, doc):
        """
        Apply naming rules for the given document. Will set `name` if the rule is matched.
        """
        if self.conditions:
            for item in self.conditions:
                if item.field == "owner":
                    index = item.index
                    if item.value != self.session.user:
                        return

            if not evaluate_filters(doc, [(self.document_type, d.field, d.condition, d.value) for d in self.conditions if d.field != "owner"]):
                return

            counter = frappe.db.get_value(self.doctype, self.name, "counter", for_update=True) or 0
            naming_series = parse_naming_series(self.prefix, doc=doc)

            doc.name = naming_series + ("%0" + str(self.prefix_digits) + "d") % (counter + 1)
            frappe.db.set_value(self.doctype, self.name, "counter", counter + 1)
