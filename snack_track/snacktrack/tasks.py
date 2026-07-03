import frappe
from frappe import _
from frappe.utils import add_days, format_date, getdate, nowdate


def get_snacktrack_manager_emails():
	return frappe.db.sql(
		"""
		select distinct u.email
		from `tabUser` u
		inner join `tabHas Role` r on r.parent = u.name
		where r.role = 'SnackTrack Manager'
			and u.enabled = 1
			and u.email is not null and u.email != ''
		""",
		as_dict=1,
	)


def send_missing_log_reminder():
	today = nowdate()
	exists = frappe.db.sql(
		"""
		select name
		from `tabDaily Refreshment Log`
		where date = %(today)s
		limit 1
		""",
		{"today": today},
		as_dict=1,
	)

	if exists:
		return

	recipients = [row.email for row in get_snacktrack_manager_emails()]
	if not recipients:
		return

	frappe.sendmail(
		recipients=recipients,
		subject=_("No Daily Refreshment Log recorded for {0}").format(format_date(today)),
		message=_(
			"No Daily Refreshment Log has been created for {0} yet. Please log today's order or "
			"confirm none was placed."
		).format(format_date(today)),
	)


def send_weekly_summary():
	today = getdate()
	week_start = add_days(today, -7)
	week_end = add_days(today, -1)

	logs = frappe.db.sql(
		"""
		select name, total_amount
		from `tabDaily Refreshment Log`
		where date between %(week_start)s and %(week_end)s
		""",
		{"week_start": week_start, "week_end": week_end},
		as_dict=1,
	)

	total_spend = sum(row.total_amount or 0 for row in logs)
	total_logs = len(logs)

	top_items = []
	if logs:
		top_items = frappe.db.sql(
			"""
			select item.item as item, sum(item.qty) as total_qty
			from `tabDaily Refreshment Item` item
			inner join `tabDaily Refreshment Log` log on log.name = item.parent
			where log.date between %(week_start)s and %(week_end)s
			group by item.item
			order by total_qty desc
			limit 5
			""",
			{"week_start": week_start, "week_end": week_end},
			as_dict=1,
		)

	recipients = [row.email for row in get_snacktrack_manager_emails()]
	if not recipients:
		return

	items_html = "".join(f"<li>{row.item} ({row.total_qty})</li>" for row in top_items) or "<li>No items ordered</li>"

	message = f"""
		<p>{_("Weekly SnackTrack summary for")} {format_date(week_start)} - {format_date(week_end)}:</p>
		<ul>
			<li>{_("Total Spend")}: {frappe.utils.fmt_money(total_spend)}</li>
			<li>{_("Number of Logs")}: {total_logs}</li>
		</ul>
		<p>{_("Top Items")}:</p>
		<ul>{items_html}</ul>
	"""

	frappe.sendmail(
		recipients=recipients,
		subject=_("SnackTrack Weekly Summary: {0} - {1}").format(
			format_date(week_start), format_date(week_end)
		),
		message=message,
	)
