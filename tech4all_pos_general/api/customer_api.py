# # customer_api.py

import frappe

# @frappe.whitelist(allow_guest=True)
# def get_customer_details(customer_name=None, mobile_no=None):
    
   
#     filters = []
    
#     if customer_name:
#         filters.append(["customer_name", "like", f"%{customer_name}%"])
#     if mobile_no:
#         filters.append(["mobile_no", "like", f"%{mobile_no}%"])
    
#     if not filters:
#         return []

#     query = """
#     SELECT *
#     FROM `tabCustomer`
#     WHERE {}
#     """.format(" OR ".join([f"{filter[0]} LIKE %s" for filter in filters]))

#     parameters = [filter[2] for filter in filters]

#     customers = frappe.db.sql(query, tuple(parameters), as_dict=True)

#     return customers

@frappe.whitelist()
def get_customer_details(customer_group=None, searchText=None):
    # Construct the SQL query to fetch all columns
    result = frappe.db.sql("""
        SELECT * 
        FROM `tabCustomer` 
        WHERE 
            (member_id = %s OR member = %s OR customer_name = %s OR rfid = %s) 
            AND (customer_group = %s OR %s IS NULL)
            AND is_member = '1' 
            AND disabled = '0'
    """, (searchText, searchText, searchText, searchText, customer_group, customer_group), as_dict=True)

    return result

import frappe
import json
from frappe import _

@frappe.whitelist(allow_guest=True)
def create_or_update_customer():
    import json

    data = frappe.local.form_dict or {}
    
    if "data" in data and isinstance(data.get("data"), str):
        data = json.loads(data.get("data"))

    if not data:
        frappe.throw(_("No data provided"))


    name = data.get("name")
    customer_name = data.get("customer_name")
    mobile_number = data.get("mobile_number")
    address_line = data.get("address")

    customer_group = data.get("customer_group")
    territory = data.get("territory")
    customer_type = data.get("customer_type") or "Company"




    try:
        # Start savepoint
        frappe.db.savepoint("customer_creation")

        # Check if updating existing Customer
        if name:
            customer = frappe.get_doc("Customer", name)
            if customer_name:
                customer.customer_name = customer_name
            if mobile_number:
                customer.mobile_no = mobile_number
            if customer_group:
                customer.customer_group = customer_group
            if territory:
                customer.territory = territory
            if data.get("customer_type"):
                customer.customer_type = customer_type
            customer.save(ignore_permissions=True)
        else:
            customer = frappe.new_doc("Customer")
            customer.customer_name = customer_name 
            customer.mobile_no = mobile_number
            customer.customer_group = customer_group
            customer.territory = territory
            customer.customer_type = customer_type
            if not mobile_number:
                    frappe.throw(_("Mobile Number is required"))
            customer.save(ignore_permissions=True)

        # Always create new Address
        if address_line:
            address = frappe.new_doc("Address")
            address.address_line1 = address_line or "Not Specified"
            address.city = "Not Specified"
            address.country = "Pakistan"
            address.is_primary_address = 1
            address.append("links", {
                "link_doctype": "Customer",
                "link_name": customer.name
            })
            address.save(ignore_permissions=True)
            customer.customer_primary_address = address.name

        if mobile_number:
            # Unset existing primary contacts
            frappe.db.sql("""
                UPDATE `tabContact` c
                JOIN `tabDynamic Link` dl ON dl.parent = c.name
                SET c.is_primary_contact = 0
                WHERE dl.link_doctype = 'Customer'
                AND dl.link_name = %s
                AND c.is_primary_contact = 1
            """, (customer.name,))


            contact_name = frappe.db.get_value("Dynamic Link", {
                "link_doctype": "Customer",
                "link_name": customer.name,
                "parenttype": "Contact"
            }, "parent")

            if contact_name:
                contact_doc = frappe.get_doc("Contact", contact_name)

                number_found = False
                for p in contact_doc.phone_nos:
                    if p.phone == mobile_number:
                        p.is_primary_mobile_no = 1
                        p.is_primary_phone = 1
                        number_found = True
                    else:
                        p.is_primary_mobile_no = 0
                        p.is_primary_phone = 0

                if not number_found:
                    for p in contact_doc.phone_nos:
                        p.is_primary_mobile_no = 0
                        p.is_primary_phone = 0
                    contact_doc.append("phone_nos", {
                        "phone": mobile_number,
                        "is_primary_phone": 1,
                        "is_primary_mobile_no": 1
                    })
                contact_doc.is_primary_contact = 1  # ensure it's primary

            else:
                contact_doc = frappe.new_doc("Contact")
                contact_doc.first_name = customer.customer_name
                contact_doc.is_primary_contact = 1
                contact_doc.append("phone_nos", {
                    "phone": mobile_number,
                    "is_primary_phone": 1,
                    "is_primary_mobile_no": 1
                })
                contact_doc.append("links", {
                    "link_doctype": "Customer",
                    "link_name": customer.name
                })

            contact_doc.save(ignore_permissions=True)
            customer.customer_primary_contact = contact_doc.name


        customer.save(ignore_permissions=True)

        
        frappe.db.commit()

        # Fetch full details properly
        address_data = []
        contact_data = []
        customer_data = frappe.get_doc("Customer", customer.name).as_dict()
        if address_line:
            address_data = frappe.get_doc("Address", address.name).as_dict()
        if mobile_number:
            contact_data = frappe.get_doc("Contact", contact_doc.name).as_dict()

        return {
            "status": "success",
            "message": "Customer created/updated successfully",
            "customer": customer_data,
            "address": address_data,
            "contact": contact_data
        }

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Customer Creation Failed")
        return {
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }
