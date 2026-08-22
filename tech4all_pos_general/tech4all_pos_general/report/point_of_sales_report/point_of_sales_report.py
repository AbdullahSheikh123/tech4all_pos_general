# Copyright (c) 2026, tech4all and contributors
# For license information, please see license.txt
"""Master POS sales report.

One report, one query engine, instead of the several near-duplicate reports
(Restaurant Sales List, Restaurant Closing Sales Report, Daily Sales Summary
Report, Dish Breakdown Summary) that each hand-rolled their own SQL for a
slightly different slice of the same data. Every "Group By" option here is a
different combination of dimensions run through the same three aggregation
paths below, so a fix (like the custom_business_date day-boundary logic) only
has to happen once.

Filtered on custom_business_date throughout, not posting_date - see that
field's description on Sales Invoice. A restaurant shift that runs past
midnight still belongs to the day it opened, and this report (like the
others) needs that to stay one day's total instead of splitting in two.
"""

import frappe
from frappe import _
from frappe.utils import flt

# Each Group By option maps to an ordered list of dimension keys. execute()
# picks one of the three aggregation levels (item, payment, header) below
# based on whether "item"/"item_group" or "mode_of_payment" is among them.
GROUP_BY_MAP = {
	"Item": ["item"],
	"Item Group": ["item_group"],
	"POS Profile": ["pos_profile"],
	"Branch": ["branch"],
	"Mode of Payment": ["mode_of_payment"],
	"POS Shift": ["pos_shift"],
	"Order Type": ["order_type"],
	"Date": ["date"],
	"Cashier": ["cashier"],
	"Sales Invoice": ["sales_invoice"],
	"Day Wise Summary": ["date"],
	"Day Wise by Shift": ["date", "pos_shift"],
	"Day Wise by Branch": ["date", "branch"],
	"Day Wise by Item": ["date", "item"],
	"Day Wise by MoP": ["date", "mode_of_payment"],
	"Day Wise by Cashier": ["date", "cashier"],
	"Day Wise by POS Profile": ["date", "pos_profile"],
	"Day Wise by Profile & Shift": ["date", "pos_profile", "pos_shift"],
	"Day Wise by Profile & MoP": ["date", "pos_profile", "mode_of_payment"],
}

# select/group SQL fragments and the report-grid column(s) for every
# dimension that isn't "item"/"item_group" (line-level) or "mode_of_payment"
# (payment-level), which are built separately since they change which table
# the query aggregates from - see get_item_level()/get_payment_level().
DIMENSIONS = {
	"pos_profile": {
		"select": ["si.pos_profile AS pos_profile"],
		"group": ["si.pos_profile"],
		"columns": [
			{"label": _("POS Profile"), "fieldname": "pos_profile", "fieldtype": "Link", "options": "POS Profile", "width": 160},
		],
	},
	"branch": {
		"select": ["b.name AS branch"],
		"group": ["b.name"],
		"columns": [
			{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 140},
		],
	},
	"pos_shift": {
		"select": ["si.posa_pos_opening_shift AS pos_shift"],
		"group": ["si.posa_pos_opening_shift"],
		"columns": [
			{"label": _("POS Shift"), "fieldname": "pos_shift", "fieldtype": "Link", "options": "POS Opening Shift", "width": 160},
		],
	},
	"order_type": {
		"select": ["si.resturent_type AS order_type"],
		"group": ["si.resturent_type"],
		"columns": [
			{"label": _("Order Type"), "fieldname": "order_type", "fieldtype": "Link", "options": "Order Type", "width": 140},
		],
	},
	"cashier": {
		"select": ["posh.user AS cashier"],
		"group": ["posh.user"],
		"columns": [
			{"label": _("Cashier"), "fieldname": "cashier", "fieldtype": "Link", "options": "User", "width": 160},
		],
	},
	"date": {
		"select": ["si.custom_business_date AS business_date"],
		"group": ["si.custom_business_date"],
		"columns": [
			{"label": _("Business Date"), "fieldname": "business_date", "fieldtype": "Date", "width": 120},
		],
	},
	"sales_invoice": {
		"select": ["si.name AS sales_invoice", "si.customer AS customer"],
		"group": ["si.name", "si.customer"],
		"columns": [
			{"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 160},
			{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 160},
		],
	},
	"item": {
		"select": ["sii.item_code AS item_code", "sii.item_name AS item_name"],
		"group": ["sii.item_code", "sii.item_name"],
		"columns": [
			{"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 140},
			{"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 180},
		],
	},
	"item_group": {
		"select": ["i.item_group AS item_group"],
		"group": ["i.item_group"],
		"columns": [
			{"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 180},
		],
	},
	"mode_of_payment": {
		"select": ["sip.mode_of_payment AS mode_of_payment"],
		"group": ["sip.mode_of_payment"],
		"columns": [
			{"label": _("Mode of Payment"), "fieldname": "mode_of_payment", "fieldtype": "Link", "options": "Mode of Payment", "width": 160},
		],
	},
}


def execute(filters=None):
	filters = frappe._dict(filters or {})

	if not filters.from_date or not filters.to_date:
		frappe.throw(_("From Date and To Date are mandatory"))

	group_by = filters.group_by or "Item"
	if group_by not in GROUP_BY_MAP:
		frappe.throw(_("Unknown Group By option: {0}").format(group_by))

	dims = GROUP_BY_MAP[group_by]
	conditions, values = get_filter_conditions(filters)

	if group_by == "Sales Invoice":
		return get_invoice_detail(conditions, values)
	if "item" in dims or "item_group" in dims:
		return get_item_level(dims, conditions, values)
	if "mode_of_payment" in dims:
		return get_payment_level(dims, conditions, values)
	return get_header_level(dims, conditions, values)


def get_filter_conditions(filters):
	"""Build WHERE conditions from the report filters.

	Every filter that isn't a plain Sales Invoice column (item, item_group,
	mode_of_payment) is expressed as an EXISTS/IN subquery rather than a join,
	even when that same dimension is also being grouped on - joining
	Sales Invoice Item or Sales Invoice Payment directly into a header-level
	aggregation would multiply si.total/grand_total by however many matching
	child rows each invoice has, silently inflating every total.
	"""
	conditions = [
		"si.docstatus = 1",
		"si.is_pos = 1",
		"si.custom_business_date >= %(from_date)s",
		"si.custom_business_date <= %(to_date)s",
	]
	values = {"from_date": filters.from_date, "to_date": filters.to_date}

	simple_filters = {
		"company": "si.company = %(company)s",
		"pos_profile": "si.pos_profile = %(pos_profile)s",
		"voucher_no": "si.name = %(voucher_no)s",
		"order_type": "si.resturent_type = %(order_type)s",
		"opening_shift": "si.posa_pos_opening_shift = %(opening_shift)s",
	}
	for key, clause in simple_filters.items():
		if filters.get(key):
			conditions.append(clause)
			values[key] = filters.get(key)

	if filters.get("branch"):
		conditions.append(
			"si.pos_profile IN (SELECT pos_profile FROM `tabBranch` WHERE name = %(branch)s)"
		)
		values["branch"] = filters.get("branch")

	if filters.get("item"):
		conditions.append(
			"si.name IN (SELECT parent FROM `tabSales Invoice Item` WHERE item_code = %(item)s)"
		)
		values["item"] = filters.get("item")

	if filters.get("item_group"):
		conditions.append(
			"""si.name IN (
				SELECT sii.parent FROM `tabSales Invoice Item` sii
				INNER JOIN `tabItem` i ON i.item_code = sii.item_code
				WHERE i.item_group = %(item_group)s
			)"""
		)
		values["item_group"] = filters.get("item_group")

	if filters.get("mode_of_payment"):
		conditions.append(
			"si.name IN (SELECT parent FROM `tabSales Invoice Payment` WHERE mode_of_payment = %(mode_of_payment)s)"
		)
		values["mode_of_payment"] = filters.get("mode_of_payment")

	return conditions, values


def dimension_sql(dims):
	"""select/group SQL fragments plus any extra joins the given dimensions
	need, for dimensions other than item/item_group/mode_of_payment."""
	select_exprs, group_exprs = [], []
	for dim in dims:
		select_exprs += DIMENSIONS[dim]["select"]
		group_exprs += DIMENSIONS[dim]["group"]

	joins = []
	if "branch" in dims:
		joins.append("INNER JOIN `tabBranch` b ON b.pos_profile = si.pos_profile")
	if "cashier" in dims:
		joins.append("LEFT JOIN `tabPOS Opening Shift` posh ON posh.name = si.posa_pos_opening_shift")

	return select_exprs, group_exprs, joins


def dim_columns(dims):
	columns = []
	for dim in dims:
		columns += DIMENSIONS[dim]["columns"]
	return columns


def append_total_row(data, columns):
	"""Sum every numeric column into one closing row, flagged is_total_row so
	the report's formatter (bold styling) and add_total_row=0 in the .json
	both stay consistent with a single, explicit total."""
	if not data:
		return data

	total_row = {"is_total_row": 1}
	# Put the "Total" label in the first text-ish column rather than
	# unconditionally columns[0] - that's sometimes a Date column (e.g. Day
	# Wise groupings), and a string there would look wrong even though the
	# datatable renders it without erroring.
	label_col = next(
		(col for col in columns if col["fieldtype"] in ("Data", "Link")), None
	)
	if label_col:
		total_row[label_col["fieldname"]] = _("Total")

	for col in columns:
		if col["fieldtype"] in ("Currency", "Float", "Int"):
			total_row[col["fieldname"]] = sum(flt(row.get(col["fieldname"])) for row in data)

	data.append(total_row)
	return data


def get_header_level(dims, conditions, values):
	"""Aggregation straight off the Sales Invoice header - used whenever the
	chosen Group By has no item or mode-of-payment dimension, so there's no
	child table to fan out across."""
	select_exprs, group_exprs, joins = dimension_sql(dims)

	query = """
		SELECT
			{select},
			COUNT(DISTINCT si.name) AS invoice_count,
			SUM(si.total) AS total,
			SUM(si.discount_amount) AS discount_amount,
			SUM(si.total_taxes_and_charges) AS tax,
			SUM(si.grand_total) AS grand_total
		FROM `tabSales Invoice` si
		{joins}
		WHERE {where}
		GROUP BY {group}
		ORDER BY {order}
	""".format(
		select=", ".join(select_exprs),
		joins=" ".join(joins),
		where=" AND ".join(conditions),
		group=", ".join(group_exprs),
		order=group_exprs[0],
	)
	data = frappe.db.sql(query, values, as_dict=True)

	columns = dim_columns(dims) + [
		{"label": _("Invoices"), "fieldname": "invoice_count", "fieldtype": "Int", "width": 90},
		{"label": _("Net Total"), "fieldname": "total", "fieldtype": "Currency", "width": 130},
		{"label": _("Discount"), "fieldname": "discount_amount", "fieldtype": "Currency", "width": 110},
		{"label": _("Tax"), "fieldname": "tax", "fieldtype": "Currency", "width": 110},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 140},
	]
	return columns, append_total_row(data, columns)


def get_item_level(dims, conditions, values):
	"""Line-level aggregation (joins Sales Invoice Item) - used for Item /
	Item Group, and any Day Wise combination that includes one of them. Qty
	and amount are summed off the item rows themselves rather than the
	invoice header, so an invoice with several items isn't counted several
	times over at header amounts."""
	item_dim = "item_group" if "item_group" in dims else "item"
	other_dims = [d for d in dims if d not in ("item", "item_group")]

	select_exprs, group_exprs, joins = dimension_sql(other_dims)
	select_exprs = DIMENSIONS[item_dim]["select"] + select_exprs
	group_exprs = DIMENSIONS[item_dim]["group"] + group_exprs

	item_master_join = (
		"INNER JOIN `tabItem` i ON i.item_code = sii.item_code" if item_dim == "item_group" else ""
	)

	query = """
		SELECT
			{select},
			SUM(sii.qty) AS qty,
			SUM(sii.base_amount) AS amount
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		{item_master_join}
		{joins}
		WHERE {where}
		GROUP BY {group}
		ORDER BY {order}
	""".format(
		select=", ".join(select_exprs),
		item_master_join=item_master_join,
		joins=" ".join(joins),
		where=" AND ".join(conditions),
		group=", ".join(group_exprs),
		order=group_exprs[0],
	)
	data = frappe.db.sql(query, values, as_dict=True)

	columns = DIMENSIONS[item_dim]["columns"] + dim_columns(other_dims) + [
		{"label": _("Qty"), "fieldname": "qty", "fieldtype": "Float", "width": 90},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 130},
	]
	return columns, append_total_row(data, columns)


def get_payment_level(dims, conditions, values):
	"""Payment-level aggregation (joins Sales Invoice Payment) - used for
	Mode of Payment and any Day Wise combination that includes it.

	sip.amount is the amount tendered on that payment row, not the amount
	actually applied to the invoice - for Cash, a customer handing over more
	than the bill (e.g. Rs 2000 for a Rs 250 total) is stored as amount=2000
	on the Cash row, with the Rs 1750 change recorded separately on the
	invoice itself as change_amount (see invoice.py::before_submit, standard
	ERPNext POS behaviour). Left uncorrected, summing sip.amount straight
	overstates Cash takings by however much change was given across the
	period. Net it out on the Cash-type row only - change is always given in
	cash, never on card/digital modes, even on a split-payment sale - so the
	total here reconciles with what actually went into the till, matching the
	header-level (POS Profile/Branch/etc.) total for the same invoices.

	A single invoice can have at most one row per distinct Mode of Payment
	(the POS UI only ever writes to pos_profile.payments.find(mode_of_payment
	=== ...), never creates a second row of the same mode), so the ordinary
	split-payment case (one Cash row + one or more non-cash rows) is exact.
	The one thing that WOULD break it is a POS Profile configured with two
	separate Modes of Payment that are both type=Cash (e.g. "Till Cash" and
	"Petty Cash") and a sale split across both - matching on sip.type alone
	would double-subtract change_amount once per row. The idx-based subquery
	below closes that off by only ever crediting the change to the single
	lowest-idx Cash row per invoice, however many Cash-typed rows it has."""
	other_dims = [d for d in dims if d != "mode_of_payment"]
	select_exprs, group_exprs, joins = dimension_sql(other_dims)
	select_exprs = DIMENSIONS["mode_of_payment"]["select"] + select_exprs
	group_exprs = DIMENSIONS["mode_of_payment"]["group"] + group_exprs

	query = """
		SELECT
			{select},
			SUM(
				sip.amount
				- CASE
					WHEN sip.type = 'Cash'
					 AND sip.idx = (
						SELECT MIN(sip2.idx) FROM `tabSales Invoice Payment` sip2
						WHERE sip2.parent = sip.parent AND sip2.type = 'Cash'
					 )
					THEN COALESCE(si.change_amount, 0)
					ELSE 0
				  END
			) AS amount
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Payment` sip ON sip.parent = si.name
		{joins}
		WHERE {where}
		GROUP BY {group}
		ORDER BY {order}
	""".format(
		select=", ".join(select_exprs),
		joins=" ".join(joins),
		where=" AND ".join(conditions),
		group=", ".join(group_exprs),
		order=group_exprs[0],
	)
	data = frappe.db.sql(query, values, as_dict=True)

	columns = DIMENSIONS["mode_of_payment"]["columns"] + dim_columns(other_dims) + [
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 140},
	]
	return columns, append_total_row(data, columns)


def get_invoice_detail(conditions, values):
	"""Sales Invoice group-by option - one row per invoice, no aggregation."""
	query = """
		SELECT
			si.name AS sales_invoice,
			si.bill_no AS bill_no,
			si.customer AS customer,
			si.custom_business_date AS business_date,
			si.posting_date AS posting_date,
			si.posting_time AS posting_time,
			si.pos_profile AS pos_profile,
			si.posa_pos_opening_shift AS pos_shift,
			si.resturent_type AS order_type,
			si.total AS total,
			si.discount_amount AS discount_amount,
			si.total_taxes_and_charges AS tax,
			si.grand_total AS grand_total
		FROM `tabSales Invoice` si
		WHERE {where}
		ORDER BY si.custom_business_date, si.posting_time
	""".format(where=" AND ".join(conditions))
	data = frappe.db.sql(query, values, as_dict=True)

	columns = [
		{"label": _("Sales Invoice"), "fieldname": "sales_invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 160},
		{"label": _("Bill No"), "fieldname": "bill_no", "fieldtype": "Int", "width": 90},
		{"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 150},
		{"label": _("Business Date"), "fieldname": "business_date", "fieldtype": "Date", "width": 110},
		{"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 110},
		{"label": _("Posting Time"), "fieldname": "posting_time", "fieldtype": "Time", "width": 100},
		{"label": _("POS Profile"), "fieldname": "pos_profile", "fieldtype": "Link", "options": "POS Profile", "width": 140},
		{"label": _("POS Shift"), "fieldname": "pos_shift", "fieldtype": "Link", "options": "POS Opening Shift", "width": 140},
		{"label": _("Order Type"), "fieldname": "order_type", "fieldtype": "Link", "options": "Order Type", "width": 120},
		{"label": _("Net Total"), "fieldname": "total", "fieldtype": "Currency", "width": 120},
		{"label": _("Discount"), "fieldname": "discount_amount", "fieldtype": "Currency", "width": 110},
		{"label": _("Tax"), "fieldname": "tax", "fieldtype": "Currency", "width": 110},
		{"label": _("Grand Total"), "fieldname": "grand_total", "fieldtype": "Currency", "width": 130},
	]
	return columns, append_total_row(data, columns)
