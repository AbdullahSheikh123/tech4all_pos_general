// Copyright (c) 2024, tech4allERP and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sales Summary"] = {
	"filters": [
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
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
            method: "tech4all_pos_general.tech4all_pos_general.report.daily_sales_summary.daily_sales_summary.get_user_branches",
            callback: function(response) {
                if (response.message) {
                    var allowed_branches = response.message;
                    var branch_filter = frappe.query_report.get_filter('pos_profile');
                    
                    if (frappe.session.user === "Administrator") {
                        allowed_branches.unshift(""); 
                    }
                    
                    branch_filter.df.options = allowed_branches;
                    
                    if (frappe.session.user !== "Administrator" && allowed_branches.length > 0) {
                        branch_filter.set_value(allowed_branches[0]);
                        frappe.query_report.refresh();
                    }
                    
                    branch_filter.refresh();
                }
            }
        });
    }
};


