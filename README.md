# SnackTrack

A [Frappe](https://frappeframework.com) app for managing office pantry, tea, coffee, and refreshment expenses.

**Publisher:** Mishhka Suthar
**License:** MIT  
**Version:** 0.0.1  
**Branch:** `version-16`

## Overview

SnackTrack helps teams track and manage shared office refreshment spending—things like pantry supplies, tea, coffee, and snacks ordered from a supplier (e.g. TeaTorium). It is built on the Frappe Framework and targets Frappe v16.

## Features

- **Daily Refreshment Log** — records date, supplier, contact, order-placer, and a line-item table of ordered items with auto-calculated amounts and totals.
- **Roles** — `SnackTrack User` (own logs only), `SnackTrack Manager` (full access), `SnackTrack Viewer` (read-only reports).
- **Validations** — blocks duplicate logs for the same supplier/date, warns on zero-amount rows, filters items by the supplier's linked item group, and defaults new rows to qty 1.
- **SnackTrack Workspace** — shortcuts to create a log or open the report, number cards for this month's spend and this week's log count, and a recent logs quick list.
- **Print Format** — a clean layout for sending monthly reconciliations to the supplier.
- **Quick Add & Copy Previous Day** — one-click buttons to add common items (Tea, Coffee, Biscuits, Water) with auto-fetched Standard Buying rates, or copy the previous day's order for the same supplier.
- **Refreshment Order Templates** — reusable per-supplier item sets that can be applied to a log in one click.
- **Reports** — Daily Refreshment Summary, Item-wise Consumption, Top 10 Items, and Monthly Trend (spend over time).
- **Calendar view** on Daily Refreshment Log to spot missing days.
- **SnackTrack Settings** — single doctype for monthly budget, default supplier, and allowed item group, with a budget-used-vs-remaining indicator.

## Requirements

- [Frappe Bench](https://github.com/frappe/bench)
- Frappe v16 (`version-16` branch)
- Python 3.14+

## Installation

Install the app on an existing bench:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/mishhka-suthar/snack_track --branch version-16
bench --site your-site.local install-app snack_track
```

To install on all sites on the bench:

```bash
bench --site all install-app snack_track
```

## Development

### Project structure

```
snack_track/
├── snack_track/
│   ├── hooks.py          # App configuration and Frappe hooks
│   ├── modules.txt       # Frappe module list (SnackTrack)
│   ├── patches.txt       # Database migration patches
│   ├── patches/          # Patch scripts
│   ├── config/           # Desk module config
│   ├── public/           # Static assets (JS, CSS, images)
│   ├── templates/        # Jinja templates
│   └── snacktrack/       # SnackTrack module
├── pyproject.toml
└── README.md
```

### Local setup

If you already have the app in your bench (for example under `apps/snack_track`):

```bash
cd apps/snack_track
pre-commit install
```

Run migrations after pulling changes:

```bash
bench --site your-site.local migrate
```

## Contributing

This app uses [pre-commit](https://pre-commit.com/) for code formatting and linting. Install and enable it before committing:

```bash
cd apps/snack_track
pip install pre-commit   # if not already installed
pre-commit install
```

Pre-commit runs the following tools:

- **ruff** — import sorting, linting, and formatting
- **eslint** — JavaScript linting
- **prettier** — JavaScript, Vue, and SCSS formatting
- Standard checks — trailing whitespace, merge conflicts, AST/JSON/TOML/YAML validation

## License

MIT — see [license.txt](license.txt).
