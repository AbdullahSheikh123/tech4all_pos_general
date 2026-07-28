from __future__ import unicode_literals
import frappe

def boot_session(bootinfo):
    try:
        document_defaults = frappe.get_all(
            "Document Defaults",
            filters={},
            fields=["name", "document_type", "user"],
        )
    except:
        document_defaults= None

    if document_defaults:
        default_ids = [default["name"] for default in document_defaults]

    try:
        child_table_rows = frappe.db.sql(
            """
            SELECT *
            FROM `tabDocument Defaults Condition`
            WHERE parent IN %(default_ids)s
            """,
            values={"default_ids": default_ids},
            as_dict=True,
        )
    except:
        child_table_rows = None
    
    if child_table_rows:
        child_table_map = {}
        for row in child_table_rows:
            parent = row["parent"]
            if parent not in child_table_map:
                child_table_map[parent] = []
            child_table_map[parent].append(row)

        for default in document_defaults:
            default["conditions"] = child_table_map.get(default["name"], [])

        bootinfo.document_defaults = document_defaults
