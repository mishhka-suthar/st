# Copyright (c) 2026, Mishhka and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_first_day, get_last_day, nowdate


class SnackTrackSettings(Document):
	pass


@frappe.whitelist()
def get_budget_status():
	settings = frappe.get_single("SnackTrack Settings")
	month_start = get_first_day(nowdate())
	month_end = get_last_day(nowdate())

	spent = frappe.db.sql(
		"""
		select sum(total_amount) as total
		from `tabDaily Refreshment Log`
		where date between %(month_start)s and %(month_end)s
		""",
		{"month_start": month_start, "month_end": month_end},
		as_dict=1,
	)

	used = flt(spent[0].total) if spent else 0
	budget = flt(settings.monthly_budget)

	return {
		"budget": budget,
		"used": used,
		"remaining": budget - used,
	}
