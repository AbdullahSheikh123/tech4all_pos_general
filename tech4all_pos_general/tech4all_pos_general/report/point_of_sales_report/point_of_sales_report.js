// Copyright (c) 2026, tech4all and contributors
// For license information, please see license.txt
/* global frappe */
/* eslint-disable */

frappe.query_reports["Point of Sales Report"] = {
	// ─────────────────────────────────────────────────────────────────────
	// FILTERS
	// ─────────────────────────────────────────────────────────────────────
	filters: [
		{
			fieldname: "from_date",
			label: __("From Business Date"),
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1,
			width: "100px",
			description: __("Restaurant trading day, not the calendar posting date - a night that runs past midnight is still counted on the day it opened."),
		},
		{
			fieldname: "to_date",
			label: __("To Business Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
			width: "100px",
		},
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			width: "120px",
		},
		{
			fieldname: "branch",
			label: __("Branch"),
			fieldtype: "Link",
			options: "Branch",
			width: "120px",
		},
		{
			fieldname: "pos_profile",
			label: __("POS Profile"),
			fieldtype: "Link",
			options: "POS Profile",
			width: "120px",
			get_query() {
				const branch = frappe.query_report.get_filter_value("branch");
				const filters = {};
				if (branch) filters.custom_branch = branch;
				return { filters };
			},
		},
		{
			// Maps to Sales Invoice.posa_pos_opening_shift on the backend -
			// "opening_shift" is just this report's own filter key.
			fieldname: "opening_shift",
			label: __("POS Opening Shift"),
			fieldtype: "Link",
			options: "POS Opening Shift",
			width: "120px",
			get_query() {
				const pos_profile = frappe.query_report.get_filter_value("pos_profile");
				const filters = {};
				if (pos_profile) filters.pos_profile = pos_profile;
				return { filters };
			},
		},
		{
			fieldname: "voucher_no",
			label: __("Sales Invoice"),
			fieldtype: "Link",
			options: "Sales Invoice",
			width: "160px",
		},
		{
			fieldname: "mode_of_payment",
			label: __("Mode of Payment"),
			fieldtype: "Link",
			options: "Mode of Payment",
			width: "120px",
		},
		{
			fieldname: "order_type",
			label: __("Order Type"),
			fieldtype: "Link",
			options: "Order Type",
			width: "120px",
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
			width: "120px",
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group",
			width: "120px",
		},
		{
			fieldname: "group_by",
			label: __("Group By"),
			fieldtype: "Select",
			options: [
				"Item",
				"Item Group",
				"POS Profile",
				"Branch",
				"Mode of Payment",
				"POS Shift",
				"Order Type",
				"Date",
				"Cashier",
				"Sales Invoice",
				"Day Wise Summary",
				"Day Wise by Shift",
				"Day Wise by Branch",
				"Day Wise by Item",
				"Day Wise by MoP",
				"Day Wise by Cashier",
				"Day Wise by POS Profile",
				"Day Wise by Profile & Shift",
				"Day Wise by Profile & MoP",
			].join("\n"),
			default: "Item",
			reqd: 1,
			width: "140px",
		},
	],

	// ─────────────────────────────────────────────────────────────────────
	// ON LOAD
	// ─────────────────────────────────────────────────────────────────────
	onload(report) {
		report.page.add_inner_button(__("Refresh"), function () {
			report.refresh();
		});

		// Quick group-by shortcuts in the toolbar
		const groupByOptions = [
			{ label: __("Item"), value: "Item" },
			{ label: __("Item Group"), value: "Item Group" },
			{ label: __("Branch"), value: "Branch" },
			{ label: __("POS Profile"), value: "POS Profile" },
			{ label: __("Mode of Payment"), value: "Mode of Payment" },
			{ label: __("POS Shift"), value: "POS Shift" },
			{ label: __("Order Type"), value: "Order Type" },
			{ label: __("Date"), value: "Date" },
			{ label: __("Cashier"), value: "Cashier" },
			{ label: __("Sales Invoice"), value: "Sales Invoice" },
			{ label: __("Day Wise Summary"), value: "Day Wise Summary" },
			{ label: __("Day Wise by Shift"), value: "Day Wise by Shift" },
			{ label: __("Day Wise by Branch"), value: "Day Wise by Branch" },
			{ label: __("Day Wise by Item"), value: "Day Wise by Item" },
			{ label: __("Day Wise by MoP"), value: "Day Wise by MoP" },
			{ label: __("Day Wise by Cashier"), value: "Day Wise by Cashier" },
			{ label: __("Day Wise by POS Profile"), value: "Day Wise by POS Profile" },
			{ label: __("Day Wise by Profile & Shift"), value: "Day Wise by Profile & Shift" },
			{ label: __("Day Wise by Profile & MoP"), value: "Day Wise by Profile & MoP" },
		];

		groupByOptions.forEach(({ label, value }) => {
			report.page.add_inner_button(
				label,
				() => {
					report.set_filter_value("group_by", value);
					report.refresh();
				},
				__("View By")
			);
		});
	},

	// ─────────────────────────────────────────────────────────────────────
	// FORMATTER — colour total rows, highlight top values
	// ─────────────────────────────────────────────────────────────────────
	formatter(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (data && data.is_total_row) {
			value = `<strong style="color: #2c3e50;">${value}</strong>`;
		}

		// Highlight grand_total / amount columns with a colour scale hint
		if (["grand_total", "amount"].includes(column.id) && data && !data.is_total_row) {
			const amount = parseFloat(data[column.id]) || 0;
			if (amount > 0) {
				value = `<span style="color: #1a7431; font-weight: 600;">${value}</span>`;
			}
		}

		// Highlight discount in orange/red
		if (column.id === "discount_amount" && data && !data.is_total_row) {
			const amount = parseFloat(data.discount_amount) || 0;
			if (amount > 0) {
				value = `<span style="color: #c0392b;">${value}</span>`;
			}
		}

		return value;
	},

	// ─────────────────────────────────────────────────────────────────────
	// AFTER DATATABLE RENDER — style the report summary cards, if present
	// ─────────────────────────────────────────────────────────────────────
	after_datatable_render(datatable) {
		const summaryWrapper = document.querySelector(".report-summary");
		if (!summaryWrapper) return;

		const cards = summaryWrapper.querySelectorAll(".summary-item");
		const indicatorColors = {
			Blue: "#0d6efd",
			Green: "#198754",
			Orange: "#fd7e14",
			Red: "#dc3545",
			Purple: "#6f42c1",
		};

		cards.forEach((card) => {
			const indicator = card.querySelector(".indicator-pill");
			if (!indicator) return;

			Object.entries(indicatorColors).forEach(([cls, color]) => {
				if (indicator.classList.contains(cls.toLowerCase())) {
					card.style.borderTop = `4px solid ${color}`;
					card.style.borderRadius = "8px";
					card.style.padding = "12px 16px";
					card.style.backgroundColor = "#fff";
					card.style.boxShadow = "0 2px 8px rgba(0,0,0,0.08)";
				}
			});
		});
	},
};
