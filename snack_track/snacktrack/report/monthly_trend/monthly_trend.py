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

	if filters.get("supplier"):
		conditions += " and supplier = %(supplier)s"
		values["supplier"] = filters.get("supplier")

	return frappe.db.sql(
		f"""
		select
			date_format(date, '%%Y-%%m') as month,
			sum(total_amount) as total_amount,
			count(name) as total_logs
		from `tabDaily Refreshment Log`
		where {conditions}
		group by date_format(date, '%%Y-%%m')
		order by month
		""",
		values,
		as_dict=1,
	)


def get_chart(data):
	return {
		"data": {
			"labels": [row["month"] for row in data],
			"datasets": [{"name": _("Total Spend"), "values": [row["total_amount"] for row in data]}],
		},
		"type": "line",
		"colors": ["#2980b9"],
	}


def get_columns():
	return [
		{"label": _("Month"), "fieldname": "month", "fieldtype": "Data", "width": 100},
		{"label": _("Total Logs"), "fieldname": "total_logs", "fieldtype": "Int", "width": 120},
		{
			"label": _("Total Spend"),
			"fieldname": "total_amount",
			"fieldtype": "Currency",
			"width": 150,
		},
	]
