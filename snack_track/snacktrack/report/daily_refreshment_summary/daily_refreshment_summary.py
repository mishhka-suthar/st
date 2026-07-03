# Copyright (c) 2026, snack_track and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff


def execute(filters=None):
	filters = filters or {}

	validate_filters(filters)

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)

	return columns, data, None, chart


def validate_filters(filters):
	from_date, to_date = filters.get("from_date"), filters.get("to_date")

	if not from_date or not to_date:
		frappe.throw(_("From Date and To Date are mandatory."))

	if date_diff(to_date, from_date) < 0:
		frappe.throw(_("To Date cannot be before From Date."))


def get_data(filters):
	log = frappe.qb.DocType("Daily Refreshment Log")

	query = (
		frappe.qb.from_(log)
		.select(log.name, log.date, log.supplier, log.order_by, log.total_amount)
		.where(log.date.between(filters.get("from_date"), filters.get("to_date")))
		.orderby(log.date)
	)

	if filters.get("supplier"):
		query = query.where(log.supplier == filters.get("supplier"))

	logs = query.run(as_dict=True)
	if not logs:
		return []

	items_by_log = {}
	child_rows = frappe.get_all(
		"Daily Refreshment Item",
		filters={"parent": ("in", [d.name for d in logs])},
		fields=["parent", "item", "qty"],
	)
	for row in child_rows:
		items_by_log.setdefault(row.parent, []).append(row)

	employee_names = {
		d.name: d.employee_name
		for d in frappe.get_all(
			"Employee",
			filters={"name": ("in", [d.order_by for d in logs])},
			fields=["name", "employee_name"],
		)
	}

	for log_row in logs:
		rows = items_by_log.get(log_row.name, [])
		log_row["total_qty"] = sum(row.qty for row in rows)
		log_row["items"] = ", ".join(f"{row.item} ({row.qty})" for row in rows)
		log_row["order_by"] = employee_names.get(log_row.order_by, log_row.order_by)

	return logs


def get_chart(data):
	totals_by_supplier = {}
	for row in data:
		totals_by_supplier[row["supplier"]] = totals_by_supplier.get(row["supplier"], 0) + row["total_amount"]

	return {
		"data": {
			"labels": list(totals_by_supplier.keys()),
			"datasets": [{"name": _("Total Amount"), "values": list(totals_by_supplier.values())}],
		},
		"type": "bar",
		"colors": ["#28a745"],
	}


def get_columns():
	return [
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{
			"label": _("Supplier"),
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150,
		},
		{
			"label": _("Order By"),
			"fieldname": "order_by",
			"fieldtype": "Data",
			"width": 150,
		},
		{"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 100},
		{
			"label": _("Total Amount"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 130,
		},
		{"label": _("Items"), "fieldname": "items", "fieldtype": "Data", "width": 300},
	]
