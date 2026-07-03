# Copyright (c) 2026, snack_track and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)

	return columns, data, None, chart


def get_data(filters):
	conditions = "1=1"
	values = {}

	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and log.date between %(from_date)s and %(to_date)s"
		values["from_date"] = filters.get("from_date")
		values["to_date"] = filters.get("to_date")

	rows = frappe.db.sql(
		f"""
		select
			item.item as item,
			sum(item.qty) as total_qty,
			sum(item.amount) as total_amount
		from `tabDaily Refreshment Item` item
		inner join `tabDaily Refreshment Log` log on log.name = item.parent
		where {conditions}
		group by item.item
		order by total_qty desc
		limit 10
		""",
		values,
		as_dict=1,
	)

	for idx, row in enumerate(rows, start=1):
		row["rank"] = idx

	return rows


def get_chart(data):
	return {
		"data": {
			"labels": [row["item"] for row in data],
			"datasets": [{"name": _("Total Qty"), "values": [row["total_qty"] for row in data]}],
		},
		"type": "bar",
		"colors": ["#e67e22"],
	}


def get_columns():
	return [
		{"label": _("Rank"), "fieldname": "rank", "fieldtype": "Int", "width": 60},
		{
			"label": _("Item"),
			"fieldname": "item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 250,
		},
		{"label": _("Total Qty"), "fieldname": "total_qty", "fieldtype": "Float", "width": 130},
		{
			"label": _("Total Amount"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 150,
		},
	]
