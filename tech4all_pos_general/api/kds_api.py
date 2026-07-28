import frappe
from typing import List, Dict, Any
from datetime import datetime


def parse_datetime(datetime_str):
    # Try different formats to parse the datetime string
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"Time data '{datetime_str}' does not match any expected format")

@frappe.whitelist(allow_guest= True)
def get_sales_order_by_branch(start_datetime, end_datetime,_order_by,branch=None, kds_station=None,workflow_state=None, docstatus=None, cancelled_from_app=None):
    from datetime import datetime, timedelta
    end_datetime = datetime.now()
    start_datetime = end_datetime - timedelta(days=1)
    start_date_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        # Default docstatus = 0
    if docstatus and docstatus.strip() == "0,1":
        docstatus_filter = ['in', [0, 1]]
    elif docstatus and docstatus.strip() == "1":
        docstatus_filter = 1   
    else:
        docstatus_filter = 0

    if cancelled_from_app and cancelled_from_app.strip() == "0,1":
        cancelled_from_app_filter = ['in', [0, 1]]
    elif cancelled_from_app and cancelled_from_app.strip() == "1":
        cancelled_from_app_filter = 1
    else:
        cancelled_from_app_filter = 0

    pos_users = [
        "ifra.nawaz@dagwood.com.pk",
        "bilal.rajpoot@dagwood.com.pk",
        "danish@dagwood.com.pk",
        "faheem.sarwar@dagwood.com.pk",
        "noor.fatima@dagwood.com.pk",
        "waqas.ahmad@dagwood.com.pk",
    ]
    
    filters={'docstatus': 0,'cancelled_from_app': 0,'creation': ['between', (start_date_str, end_date_str)], "owner": ["not in", pos_users]}
    if workflow_state is not None:
        filters['workflow_state'] = workflow_state

    if branch:
        filters['branch'] = branch

    sales_orders = frappe.get_all('Sales Order',
                                 filters= filters,
                                  fields=['name'],
                                  order_by='creation '+_order_by)

    sales_orders_data = []

    for so in sales_orders:
        sales_order = frappe.get_doc("Sales Order", so.name)
        sales_order_data = sales_order.as_dict()
        sales_order_data["items"] = [] 

        for item in sales_order.items:
            item_dict = item.as_dict()

            if not item.is_stock_item:
                product_bundle = frappe.get_all('Product Bundle', filters={'new_item_code': item.item_code}, fields=['name'])

                if product_bundle:
                    bundle_name = product_bundle[0].name
                    item_specifics = frappe.get_all('Item Specifics Child', filters={'parent': bundle_name}, fields=['item_specifics_name'])
                    
                    item_specifics_list = [child.item_specifics_name for child in item_specifics]

                    item_dict['item_specifics'] = item_specifics_list

            sales_order_data["items"].append(item_dict)
        sales_orders_data.append(sales_order_data)

    return sales_orders_data  

@frappe.whitelist()
def get_sales_order(start_datetime, end_datetime,_order_by):
    if isinstance(start_datetime, str):
        start_datetime = parse_datetime(start_datetime)
    if isinstance(end_datetime, str):
        end_datetime = parse_datetime(end_datetime)
    
    start_date_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')

    sales_orders = frappe.get_all('Sales Order',
                                  filters={'docstatus': 0,'cancelled_from_app': 0,'creation': ['between', (start_date_str, end_date_str)]},
                                  fields=['name'],
                                  order_by='creation '+_order_by)

    sales_orders_data = []

    for so in sales_orders:
        sales_order = frappe.get_doc("Sales Order", so.name)
        sales_order_data = sales_order.as_dict()
        sales_orders_data.append(sales_order_data)

    return sales_orders_data   

@frappe.whitelist()
def get_pos_profile_and_branch(user_id, is_multiple_pos_profiles):
    # Debugging output to check the type and value of is_multiple_pos_profiles

    # Step 1: Get the POS Profile for the user
    user_pos_profile = frappe.get_all(
        'POS Profile User',
        filters={'user': user_id},
        fields=['parent']
    )

    if not user_pos_profile:
        return {"error": "No POS Profile found for the user."}

    pos_profile_name = user_pos_profile[0].parent

    # Fetch the full POS Profile document
    pos_profile_doc = frappe.get_doc('POS Profile', pos_profile_name)

    # Step 2: Find the corresponding branch based on the POS Profile
    branch = None  # Initialize branch variable

    if is_multiple_pos_profiles == "1":
        # Multiple profiles, check in Branch POS Profiles
        branch_data = frappe.get_all(
            'Branch POS Profiles',
            filters={'pos_profile': pos_profile_name},
            fields=['parent'],
            limit=1  # Get only one branch
        )
        if branch_data:
            branch_name = branch_data[0].parent
            # Fetch the full Branch document
            branch_doc = frappe.get_doc('Branch', branch_name)
        else:
            branch_doc = None
    elif is_multiple_pos_profiles == "0":
        # Single profile, direct link
        branch_data = frappe.get_all(
            'Branch',
            filters={'pos_profile': pos_profile_name},
            fields=['name'],
            limit=1  # Get only one branch
        )
        if branch_data:
            branch_name = branch_data[0].name
            # Fetch the full Branch document
            branch_doc = frappe.get_doc('Branch', branch_name)
        else:
            branch_doc = None
    else:
        return {"error": "Invalid value for is_multiple_pos_profiles."}

    # Return the full pos_profile_doc and branch_doc
    return {
        'pos_profile': pos_profile_doc,
        'branch': branch_doc if branch_doc else "No branch found"
    }



@frappe.whitelist(allow_guest=False)
def update_sales_order_kds_item_status(item_status_list=None, kds_status_list=None):
    """
    API to update KDS Item Status and KDS Status child tables in a Sales Order.
    Args:
        item_status_list (list): List of dicts with {name, status, start_time, end_time} for KDS Item Status.
        kds_status_list (list): List of dicts with {name, status, start_time, end_time} for KDS Status.
    Returns:
        dict: Updated Sales Order document.
    """
    try:
        # Validate input parameters
        if not item_status_list and not kds_status_list:
            frappe.throw(_("At least one of item_status_list or kds_status_list must be provided."))

        # Parse input lists (they might come as JSON strings if sent via POST)
        if isinstance(item_status_list, str):
            item_status_list = frappe.parse_json(item_status_list)
        if isinstance(kds_status_list, str):
            kds_status_list = frappe.parse_json(item_status_list)

        # Ensure lists are provided as lists
        item_status_list = item_status_list or []
        kds_status_list = kds_status_list or []

        # Validate list contents
        for item in item_status_list:
            if not isinstance(item, dict) or "name" not in item:
                frappe.throw(_("Each entry in item_status_list must be a dictionary with a 'name' key."))
        for item in kds_status_list:
            if not isinstance(item, dict) or "name" not in item:
                frappe.throw(_("Each entry in kds_status_list must be a dictionary with a 'name' key."))

        # Find the Sales Order by looking up the parent of the child table rows
        parent_sales_order = None
        if item_status_list:
            first_item_name = item_status_list[0].get("name")
            parent_sales_order = frappe.db.get_value("KDS Item Status", first_item_name, "parent")
        elif kds_status_list:
            first_kds_name = kds_status_list[0].get("name")
            parent_sales_order = frappe.db.get_value("KDS Status", first_kds_name, "parent")

        if not parent_sales_order:
            frappe.throw(_("Could not determine the parent Sales Order. Ensure the provided names exist."))

        # Load the Sales Order document
        sales_order = frappe.get_doc("Sales Order", parent_sales_order)
        if not sales_order:
            frappe.throw(_("Sales Order {0} not found.").format(parent_sales_order))

        # Update KDS Item Status child table
        for item in item_status_list:
            item_name = item.get("name")
            # Find the child table row
            for row in sales_order.get("kds_item_status", []):
                if row.name == item_name:
                    row.status = item.get("status", row.status)
                    row.start_time = item.get("start_time", row.start_time)
                    row.end_time = item.get("end_time", row.end_time)
                    break
            else:
                frappe.throw(_("KDS Item Status with name {0} not found in Sales Order {1}.").format(item_name, parent_sales_order))

        # Update KDS Status child table
        for item in kds_status_list:
            kds_name = item.get("name")
            # Find the child table row
            for row in sales_order.get("kds_status_table", []):
                if row.name == kds_name:
                    row.status = item.get("status", row.status)
                    row.start_time = item.get("start_time", row.start_time)
                    row.end_time = item.get("end_time", row.end_time)
                    break
            else:
                frappe.throw(_("KDS Status with name {0} not found in Sales Order {1}.").format(kds_name, parent_sales_order))

        # Update overall kds_status if necessary
        if sales_order.kds_status_table:
            all_cooked = all(row.status == 'Cooked' for row in sales_order.kds_status_table)
            sales_order.kds_status = 'Cooked' if all_cooked else ''
        else:
            sales_order.kds_status = ''

        # Save the Sales Order
        sales_order.save()

        # Log success
        frappe.log_error(f"Updated KDS Item Status and KDS Status for Sales Order {parent_sales_order}", "KDS API Debug")

        # Return the updated Sales Order
        return sales_order.as_dict()

    except Exception as e:
        # Log error
        frappe.log_error(
            message=f"Error in update_sales_order_kds_item_status: {str(e)}",
            title="KDS API Failure"
        )
        frappe.throw(str(e))
