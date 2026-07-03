# Copyright (c) 2026, Mishhka and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, get_link_to_form


class DailyRefreshmentLog(Document):
	def validate(self):
		self.calculate_totals()
		self.check_duplicate_log()
		self.warn_on_zero_amount()

	def calculate_totals(self):
		total_qty = 0
		total_amount = 0.0

		for row in self.items:
			row.amount = flt(row.qty) * flt(row.rate)
			total_qty += flt(row.qty)
			total_amount += row.amount

		self.total_qty = total_qty
		self.total_amount = total_amount

	def check_duplicate_log(self):
		existing = frappe.db.sql(
			"""
			select name
			from `tabDaily Refreshment Log`
			where date = %(date)s
				and supplier = %(supplier)s
				and name != %(name)s
			limit 1
			""",
			{"date": self.date, "supplier": self.supplier, "name": self.name or ""},
			as_dict=1,
		)

		if existing:
			log_link = get_link_to_form("Daily Refreshment Log", existing[0].name)
			frappe.throw(
				_("A log for {0} on {1} already exists ({2}). Open it instead?").format(
					self.supplier, frappe.utils.formatdate(self.date), log_link
				)
			)

	def warn_on_zero_amount(self):
		if any(flt(row.amount) == 0 for row in self.items):
			frappe.msgprint(
				_("One or more rows have an amount of 0. Please check quantity and rate."),
				indicator="orange",
				alert=True,
			)


@frappe.whitelist()
def search_items_by_keyword(keyword):
	return frappe.db.sql(
		"""
		select name, item_name
		from `tabItem`
		where disabled = 0
			and (item_name like %(kw)s or name like %(kw)s or item_group like %(kw)s)
		order by item_name
		limit 20
		""",
		{"kw": f"%{keyword}%"},
		as_dict=1,
	)


@frappe.whitelist()
def get_standard_buying_rate(item_code):
	rate = frappe.db.sql(
		"""
		select price_list_rate
		from `tabItem Price`
		where item_code = %(item_code)s
			and price_list = 'Standard Buying'
			and buying = 1
		order by valid_from desc
		limit 1
		""",
		{"item_code": item_code},
		as_dict=1,
	)
	return flt(rate[0].price_list_rate) if rate else 0


@frappe.whitelist()
def get_previous_day_items(supplier, current_log=None):
	condition = "and name != %(current_log)s" if current_log else ""
	previous_log = frappe.db.sql(
		f"""
		select name
		from `tabDaily Refreshment Log`
		where supplier = %(supplier)s
			{condition}
		order by date desc, creation desc
		limit 1
		""",
		{"supplier": supplier, "current_log": current_log},
		as_dict=1,
	)

	if not previous_log:
		return []

	return frappe.db.sql(
		"""
		select item, qty, rate
		from `tabDaily Refreshment Item`
		where parent = %(parent)s
		order by idx
		""",
		{"parent": previous_log[0].name},
		as_dict=1,
	)


@frappe.whitelist()
def get_template_items(template):
	return frappe.db.sql(
		"""
		select item, qty, rate
		from `tabRefreshment Order Template Item`
		where parent = %(parent)s
		order by idx
		""",
		{"parent": template},
		as_dict=1,
	)
