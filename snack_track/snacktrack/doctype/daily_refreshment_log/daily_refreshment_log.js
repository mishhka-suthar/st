// Copyright (c) 2026, Mishhka and contributors
// For license information, please see license.txt

const DAILY_REFRESHMENT_LOG_METHOD_PATH =
	"snack_track.snacktrack.doctype.daily_refreshment_log.daily_refreshment_log";
const QUICK_ADD_ITEMS = ["Tea", "Coffee", "Sandwich", "Water"];

function calculate_totals(frm) {
	let total_qty = 0;
	let total_amount = 0;

	(frm.doc.items || []).forEach((row) => {
		row.amount = flt(row.qty) * flt(row.rate);
		total_qty += flt(row.qty);
		total_amount += row.amount;
	});

	frm.set_value("total_qty", total_qty);
	frm.set_value("total_amount", total_amount);
	frm.refresh_field("items");
}

function show_stats(frm) {
	frm.dashboard.clear_headline();

	if (!(frm.doc.items || []).length) {
		return;
	}

	frm.dashboard.set_headline_alert(
		`<div class="row text-muted">
			<div class="col-xs-4"><b>${frm.doc.items.length}</b> item(s)</div>
			<div class="col-xs-4"><b>${frm.doc.total_qty || 0}</b> qty</div>
			<div class="col-xs-4"><b>${format_currency(frm.doc.total_amount || 0)}</b> total</div>
		</div>`
	);
}

function set_default_supplier(frm) {
	if (!frm.is_new() || frm.doc.supplier) {
		return;
	}

	frappe.call({
		method: "snack_track.snacktrack.doctype.snacktrack_settings.snacktrack_settings.get_default_supplier",
	}).then((r) => {
		if (r.message) {
			frm.set_value("supplier", r.message);
		}
	});
}

function set_allowed_item_group(frm) {
	frappe.db.get_single_value("SnackTrack Settings", "allowed_item_group").then((item_group) => {
		frm.doc.__allowed_item_group = item_group;
	});
}

function set_item_filter(frm) {
	frm.fields_dict.items.grid.get_field("item").get_query = () => {
		if (frm.doc.__snacktrack_item_group) {
			return { filters: { item_group: frm.doc.__snacktrack_item_group } };
		}
		if (frm.doc.__allowed_item_group) {
			return { filters: { item_group: ["descendants of (inclusive)", frm.doc.__allowed_item_group] } };
		}
		return {};
	};

	if (!frm.doc.supplier) {
		frm.doc.__snacktrack_item_group = null;
		return;
	}

	frappe.db.get_value("Supplier", frm.doc.supplier, "snacktrack_item_group").then((r) => {
		frm.doc.__snacktrack_item_group = r.message && r.message.snacktrack_item_group;
	});
}

function add_quick_item(frm, item_code) {
	const row = frm.add_child("items", { item: item_code, qty: 1 });
	frm.refresh_field("items");
	calculate_totals(frm);
	show_stats(frm);

	frappe.call({
		method: `${DAILY_REFRESHMENT_LOG_METHOD_PATH}.get_standard_buying_rate`,
		args: { item_code },
	}).then((r) => {
		frappe.model.set_value(row.doctype, row.name, "rate", r.message || 0);
		calculate_totals(frm);
		show_stats(frm);
	});
}

function pick_quick_item(frm, keyword, matches) {
	const dialog = new frappe.ui.Dialog({
		title: __("Select {0} Item", [keyword]),
		fields: [
			{
				fieldname: "item",
				fieldtype: "Link",
				label: __("Item"),
				options: "Item",
				reqd: 1,
				get_query: () => ({ filters: { name: ["in", matches.map((m) => m.name)] } }),
			},
		],
		primary_action_label: __("Add"),
		primary_action: (values) => {
			add_quick_item(frm, values.item);
			dialog.hide();
		},
	});
	dialog.show();
}

function add_quick_category(frm, keyword) {
	frappe.call({
		method: `${DAILY_REFRESHMENT_LOG_METHOD_PATH}.search_items_by_keyword`,
		args: { keyword },
	}).then((r) => {
		const matches = r.message || [];
		if (!matches.length) {
			frappe.msgprint(
				__("No item found in the Item master matching {0}.", [keyword])
			);
		} else if (matches.length === 1) {
			add_quick_item(frm, matches[0].name);
		} else {
			pick_quick_item(frm, keyword, matches);
		}
	});
}

function setup_quick_add_buttons(frm) {
	if (frm.doc.docstatus !== 0) {
		return;
	}
	QUICK_ADD_ITEMS.forEach((keyword) => {
		frm.fields_dict.items.grid.add_custom_button(
			__(keyword),
			() => add_quick_category(frm, keyword),
			"top"
		);
	});
}

function setup_copy_previous_day_button(frm) {
	if (frm.doc.docstatus !== 0 || !frm.doc.supplier) {
		return;
	}

	frm.add_custom_button(__("Copy Previous Day"), () => {
		frappe.call({
			method: `${DAILY_REFRESHMENT_LOG_METHOD_PATH}.get_previous_day_items`,
			args: { supplier: frm.doc.supplier, current_log: frm.doc.name },
		}).then((r) => {
			const rows = r.message || [];
			if (!rows.length) {
				frappe.msgprint(__("No previous log found for this supplier."));
				return;
			}
			frm.clear_table("items");
			rows.forEach((row) => {
				frm.add_child("items", { item: row.item, qty: row.qty, rate: row.rate });
			});
			frm.refresh_field("items");
			calculate_totals(frm);
			show_stats(frm);
		});
	});
}

function setup_apply_template_button(frm) {
	if (frm.doc.docstatus !== 0) {
		return;
	}

	frm.add_custom_button(__("Apply Template"), () => {
		const dialog = new frappe.ui.Dialog({
			title: __("Apply Template"),
			fields: [
				{
					fieldname: "template",
					fieldtype: "Link",
					label: __("Template"),
					options: "Refreshment Order Template",
					reqd: 1,
					get_query: () => {
						if (!frm.doc.supplier) {
							return {};
						}
						return { filters: { supplier: frm.doc.supplier } };
					},
				},
			],
			primary_action_label: __("Apply"),
			primary_action: (values) => {
				frappe.call({
					method: `${DAILY_REFRESHMENT_LOG_METHOD_PATH}.get_template_items`,
					args: { template: values.template },
				}).then((r) => {
					const rows = r.message || [];
					frm.clear_table("items");
					rows.forEach((row) => {
						frm.add_child("items", { item: row.item, qty: row.qty, rate: row.rate });
					});
					frm.refresh_field("items");
					calculate_totals(frm);
					show_stats(frm);
					dialog.hide();
				});
			},
		});
		dialog.show();
	});
}

frappe.ui.form.on("Daily Refreshment Log", {
	onload(frm) {
		set_default_supplier(frm);
		set_allowed_item_group(frm);
	},
	refresh(frm) {
		show_stats(frm);
		set_item_filter(frm);
		setup_quick_add_buttons(frm);
		setup_copy_previous_day_button(frm);
		setup_apply_template_button(frm);
	},
	supplier(frm) {
		set_item_filter(frm);
		setup_copy_previous_day_button(frm);
	},
	items_add(frm, cdt, cdn) {
		const row = frappe.get_doc(cdt, cdn);
		if (!row.qty) {
			frappe.model.set_value(cdt, cdn, "qty", 1);
		}
		calculate_totals(frm);
		show_stats(frm);
	},
	items_remove(frm) {
		calculate_totals(frm);
		show_stats(frm);
	},
});

frappe.ui.form.on("Daily Refreshment Item", {
	qty(frm) {
		calculate_totals(frm);
		show_stats(frm);
	},
	rate(frm) {
		calculate_totals(frm);
		show_stats(frm);
	},
});
