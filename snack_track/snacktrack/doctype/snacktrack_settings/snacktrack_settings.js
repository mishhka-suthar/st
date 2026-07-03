// Copyright (c) 2026, Mishhka and contributors
// For license information, please see license.txt

frappe.ui.form.on("SnackTrack Settings", {
	refresh(frm) {
		frm.dashboard.clear_headline();

		if (!frm.doc.monthly_budget) {
			return;
		}

		frappe.call({
			method: "snack_track.snacktrack.doctype.snacktrack_settings.snacktrack_settings.get_budget_status",
		}).then((r) => {
			const data = r.message || {};
			const indicator = data.remaining < 0 ? "red" : data.remaining < data.budget * 0.2 ? "orange" : "green";

			frm.dashboard.set_headline_alert(
				`<div class="row text-muted">
					<div class="col-xs-4"><b>${format_currency(data.budget || 0)}</b> budget</div>
					<div class="col-xs-4"><b>${format_currency(data.used || 0)}</b> used</div>
					<div class="col-xs-4 text-${indicator}"><b>${format_currency(data.remaining || 0)}</b> remaining</div>
				</div>`
			);
		});
	},
});
