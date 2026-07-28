frappe.realtime.on('sales_order_kds_item_status_update', (data) => {
    console.log('Received data:', data);

    if (data && data.sales_order_name && data.new_status && data.row_name) {
        let sales_order_name = data.sales_order_name;
        let new_status = data.new_status;
        let row_name = data.row_name;

        update_status_in_sales_order(sales_order_name, row_name, new_status);
    }
});

frappe.realtime.on('sales_order_kds_status_update', (data) => {
    console.log('Received data:', data);

    if (data && data.sales_order_name && data.new_status && data.row_name) {
        let sales_order_name = data.sales_order_name;
        let new_status = data.new_status;
        let row_name = data.row_name;

        update_kds_status_in_sales_order(sales_order_name, row_name, new_status);
    }
});

function update_status_in_sales_order(sales_order_name, row_name, new_status) {
    frappe.call({
        method: 'tech4all_pos_general.custom.sales_order_custom.update_status_in_sales_order',
        args: {
            sales_order_name: sales_order_name,
            new_status: new_status,
            row_name: row_name
        },
        callback: function(response) {
            if (response.message) {
                console.log(response.message);
                frappe.msgprint('Status updated successfully!');
            } else {
                console.log("No message received.");
            }
        }
    });
}

function update_kds_status_in_sales_order(sales_order_name, row_name, new_status) {
    frappe.call({
        method: 'tech4all_pos_general.custom.sales_order_custom.update_kds_status_in_sales_order',
        args: {
            sales_order_name: sales_order_name,
            new_status: new_status,
            row_name: row_name
        },
        callback: function(response) {
            if (response.message) {
                console.log(response.message);
                frappe.msgprint('KDS status updated successfully!');
            } else {
                console.log("No message received.");
            }
        }
    });
}
