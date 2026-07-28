import frappe

def validate(self, m=None):
    self.order_time = max((i.cooking_time for i in self.items if i.is_kds_item), default=1500)
    
    if self.table_no:
        table = frappe.get_doc("Table Management", self.table_no)
        if self.cancelled_from_app:
            table.status = "Available"
        else:
            table.status = "Reserved"
        table.save()

def on_submit(self, m=None):
    # Set the table status to Available on submit
    if self.table_no:
        table = frappe.get_doc("Table Management", self.table_no)
        table.status = "Available"
        table.save()

def after_insert(doc, method):
    sales_order_data = doc.as_dict()
    frappe.publish_realtime('new_sales_order', sales_order_data, user=frappe.session.user)


@frappe.whitelist()
def update_status_in_sales_order(sales_order_name, row_name, new_status):
    try:
        query = """
            UPDATE `tabKDS Item Status`
            SET status = %s
            WHERE parent = %s AND name = %s;
        """
        
        frappe.db.sql(query, (new_status, sales_order_name, row_name))

        frappe.db.commit()

        frappe.publish_realtime('sales_order_kds_item_status_update', data={
            'sales_order_name': sales_order_name,
            'row_name': row_name,
            'new_status': new_status,
            'status':'success'
        })

        return True
    except Exception as e:
        frappe.publish_realtime('sales_order_kds_item_status_update', data={
            'sales_order_name': sales_order_name,
            'row_name': row_name,
            'new_status': new_status,
            'status':'Failed'
        })
        frappe.log_error(f"Error updating status for Sales Order {sales_order_name} and row {row_name}: {str(e)}", "KDS Item Status Update Error")
        return False

@frappe.whitelist()
def update_kds_status_in_sales_order(sales_order_name, row_name, new_status):
    try:
        query = """
            UPDATE `tabKDS Status`
            SET status = %s
            WHERE parent = %s AND name = %s;
        """
        
        frappe.db.sql(query, (new_status, sales_order_name, row_name))

        frappe.db.commit()

        frappe.publish_realtime('sales_order_kds_status_update', data={
            'sales_order_name': sales_order_name,
            'row_name': row_name,
            'new_status': new_status,
            'status':'success'
        })

        return True
    except Exception as e:
        frappe.publish_realtime('sales_order_kds_status_update', data={
            'sales_order_name': sales_order_name,
            'row_name': row_name,
            'new_status': new_status,
            'status':'Failed'
        })
        frappe.log_error(f"Error updating status for Sales Order {sales_order_name} and row {row_name}: {str(e)}", "KDS Item Status Update Error")
        return False
