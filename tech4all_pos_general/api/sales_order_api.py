import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def get_sales_order_details(customer, limit_start, limit_page_length, order_by='desc'):
    sales_order_meta = frappe.get_meta('Sales Order')
    fields = [field.fieldname for field in sales_order_meta.fields]
    
    sales_orders = frappe.get_all('Sales Order',
                                  filters={'customer': customer},
                                  fields=['name'],
                                  order_by='creation ' + order_by,
                                  limit_start=int(limit_start),
                                  limit_page_length=int(limit_page_length))

    sales_orders_data = []

    for so in sales_orders:
        sales_order = frappe.get_doc("Sales Order", so.name)
        sales_order_data = sales_order.as_dict()
        
        if 'items' in sales_order_data:
            sales_order_data['items'] = [item.as_dict() for item in sales_order.items]
        
        sales_orders_data.append(sales_order_data)

    return sales_orders_data

@frappe.whitelist(allow_guest=True)
def get_sales_order_with_item_specifics(sales_order_name):
   
    sales_order = frappe.get_doc("Sales Order", sales_order_name)
    
    response = sales_order.as_dict() 

    response["items"] = [] 

    for item in sales_order.items:
        item_dict = item.as_dict()

        if not item.is_stock_item:
            product_bundle = frappe.get_all('Product Bundle', filters={'new_item_code': item.item_code}, fields=['name'])

            if product_bundle:
                bundle_name = product_bundle[0].name
                item_specifics = frappe.get_all('Item Specifics Child', filters={'parent': bundle_name}, fields=['item_specifics_name'])
                
                item_specifics_list = [child.item_specifics_name for child in item_specifics]
                item_dict['product_bundle'] = product_bundle[0]
                item_dict['item_specifics'] = item_specifics_list

        response["items"].append(item_dict)

    return response



@frappe.whitelist()
def get_sales_order_by_branch(start_datetime, end_datetime,_order_by,branch=None, kds_station=None,workflow_state=None,docstatus=None, cancelled_from_app=None):
    from datetime import datetime, timedelta
    end_datetime = datetime.now()
    start_datetime = end_datetime - timedelta(days=1)
    start_date_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')
    
    filters={'creation': ['between', (start_date_str, end_date_str)]}
    if docstatus is not None:
        filters['docstatus'] = docstatus
    if cancelled_from_app is not None:
        filters['cancelled_from_app'] = cancelled_from_app
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

