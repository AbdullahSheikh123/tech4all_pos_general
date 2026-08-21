// Copyright (c) 2024, tech4all and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Restaurant Sales List"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Business Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1,
            "description": __("Restaurant trading day, not the calendar posting date - a night that runs past midnight is still counted on the day it opened.")
        },
        {
            "fieldname": "to_date",
            "label": __("To Business Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
			"fieldname":"pos_profile",
			"label": __("Branch"),
			"fieldtype": "Select",
			"options": [],
		}
    ],
    onload: function() {
        // Fetch allowed branches for the current user
        frappe.call({
            method: "tech4all_pos_general.tech4all_pos_general.report.restaurant_sales_list.restaurant_sales_list.get_user_branches",
            callback: function(response) {
                if (response.message) {
                    var allowed_branches = response.message;
                    var branch_filter = frappe.query_report.get_filter('pos_profile');
                    branch_filter.df.options = allowed_branches;
                    branch_filter.refresh();
                }
            }
        });
    }
};
