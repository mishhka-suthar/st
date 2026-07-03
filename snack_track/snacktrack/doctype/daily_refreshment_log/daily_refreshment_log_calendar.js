// Copyright (c) 2026, Mishhka and contributors
// For license information, please see license.txt

frappe.views.calendar["Daily Refreshment Log"] = {
	field_map: {
		start: "date",
		end: "date",
		id: "name",
		title: "supplier",
		allDay: 1,
	},
	filters: [
		{
			fieldtype: "Link",
			fieldname: "supplier",
			options: "Supplier",
			label: __("Supplier"),
		},
	],
	get_events_method: "frappe.desk.calendar.get_events",
};
