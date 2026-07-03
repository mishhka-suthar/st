// Copyright (c) 2026, snack_track and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Trend"] = {
	filters: [
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier",
		},
	],
};
