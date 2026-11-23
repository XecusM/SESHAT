<p align="center">
  <img src="./seshat/static/images/logo.png" alt="SESHAT - inventory management" width="360">
</p>

<p align="center">
  <strong>Open source inventory management for small businesses.</strong><br>
  Know what you have, where it is, what you bought and what you sold, in English or Arabic, by day or by night.
</p>

<p align="center">
  <img alt="Python 3.13" src="https://img.shields.io/badge/python-3.13-3d6e78">
  <img alt="Django 6.1" src="https://img.shields.io/badge/django-6.1-3d6e78">
  <img alt="Bootstrap 5.3" src="https://img.shields.io/badge/bootstrap-5.3.8-a9804f">
  <img alt="Font Awesome 7" src="https://img.shields.io/badge/font%20awesome-7.3.1-a9804f">
  <img alt="Tests" src="https://img.shields.io/badge/tests-375%20passing-3f7d52">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-2a2320">
</p>

---

> *Seshat was the ancient Egyptian goddess of writing, measurement and record keeping:
> the scribe who counted everything. This SESHAT counts your stock.*

## ✨ Why SESHAT?

- 📦 **Stock that adds up.** Every quantity comes from a recorded move (purchase, sale,
  transfer or a custom adjustment), and SESHAT refuses any move that would make a shelf go negative.
- 🧩 **Assembled items.** Build kits from components; selling a kit takes its parts out of stock automatically.
- 🏬 **Locations and sub-locations.** Warehouses, rooms and shelves, with quantities per shelf
  and one-click transfers between them.
- 🧾 **Purchase and sale orders.** Line items, invoice details, live totals and printable order sheets.
- 🤝 **Customers and vendors.** Companies and their contacts, with the full order history of each one.
- 📊 **Dashboards.** Stock value, low-stock alerts, purchases vs. sales charts and activity reports.
- 🔐 **Fine-grained permissions.** Per-module view/add/edit/delete permissions, managed from one screen.
- 🕵️ **Complete audit trail.** Every create, edit, delete, import and backup is logged with who and when.
- 💾 **Your data, portable.** One-click JSON backups and restore, plus CSV import/export with ready-made templates.
- 🌍 **Bilingual.** English and Arabic, with a full right-to-left layout.
- 🌙 **Night mode.** Light, dark, or follow the system, chosen per user and switched from the navbar.
- 🪶 **Lightweight.** Plain Django and SQLite out of the box, no Node build step, works offline.

## 🧱 Tech stack

| | |
|---|---|
| Backend | Python 3.13, Django 6.1, Django REST framework |
| Frontend | Bootstrap 5.3.8, Font Awesome 7.3.1, Chart.js, Cropper.js, vanilla JavaScript |
| Activity log | [`x-django-app`](https://pypi.org/project/x-django-app/) (`XActivity`, `XListView`, `XCreateView`, `XUpdateView`) |
| Error log | `django-db-logger` (server errors are stored and shown in the admin dashboard) |
| Forms | `django-crispy-forms` + `crispy-bootstrap5` |
| Database | SQLite by default; any Django-supported database through settings |

## 🗂️ Project layout

```
seshat/                  Django project root (manage.py lives here)
├── seshat/              Project package: settings, urls, dashboard, backup/restore,
│                        CSV import/export engine, error pages, shared helpers
├── account/             Users, profiles, photos, settings (language, theme), permissions,
│                        activities, activity reports and log entries
├── stock/               Items, assembled items, categories, locations, moves and transfers
│   ├── models/ forms/ views/ urls/      split by domain: categories, locations, items, moves
│   └── tests/test_categories/ test_locations/ test_items/ test_moves/
├── customer/            Customers' companies and contacts
├── vendor/              Vendors' companies and contacts
├── purchase/            Purchase orders (add stock)
├── sale/                Sale orders (remove stock)
├── templates/           Base layout, shared components and error pages (400/403/404/405/500)
├── static/              Bootstrap, Font Awesome, theme CSS and JavaScript (vendored, no CDN)
└── locale/ar/           Arabic translation
```

## 🚀 Getting started

```bash
git clone https://github.com/XecusM/SESHAT.git
cd SESHAT/seshat
python3.13 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py compilemessages   # needs GNU gettext, for the Arabic interface
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> and sign in.

> **Why `makemigrations`?** Migration files are not committed, so every installation
> generates its own. The same command also creates the missing initial migration of
> `x-django-app` 1.2.2, whose published package doesn't include it.

## ⚙️ Configuration

Settings are read from environment variables, or from a `.env` file placed next to `manage.py`:

| Variable | Default | Description |
|---|---|---|
| `SESHAT_DEBUG` | `true` | Turn off in production |
| `SESHAT_SECRET_KEY` | development key | **Required** when debug is off |
| `SESHAT_ALLOWED_HOSTS` | `*` (debug) | Comma separated host names |
| `SESHAT_CSRF_TRUSTED_ORIGINS` | empty | e.g. `https://stock.example.com` |
| `SESHAT_HTTPS` | on when debug is off | Secure cookies, HTTPS redirect and HSTS; set `false` if you serve plain HTTP |
| `SESHAT_TIME_ZONE` | `Africa/Cairo` | Any IANA time zone |
| `SESHAT_DB_ENGINE` / `_NAME` / `_USER` / `_PASSWORD` / `_HOST` / `_PORT` | SQLite file | Database connection |
| `SESHAT_VAR_DIR` | `seshat/var` | Where backups, restores, imports and exports are kept |

Example `.env`:

```dotenv
SESHAT_DEBUG=false
SESHAT_SECRET_KEY=change-me-to-a-long-random-string
SESHAT_ALLOWED_HOSTS=stock.example.com
SESHAT_CSRF_TRUSTED_ORIGINS=https://stock.example.com
```

For production, also run `python manage.py collectstatic` and serve `staticroot/` and `media/`
from your web server.

## 🌙 Night mode & 🌍 languages

Each user picks a **Theme** (Auto, Light or Dark), a **Language**, a page size and a
favorite landing page under *My account → Settings*. The half-moon button in the navbar switches
between light and dark instantly; the language button switches between English and العربية.
Arabic pages use Bootstrap's right-to-left stylesheet.

To add a language: add it to `LANGUAGES` in `seshat/settings.py`, then run
`python manage.py makemessages -l <code>`, translate `locale/<code>/LC_MESSAGES/django.po`
and run `compilemessages`.

## 🧪 Tests

Every application has unit tests for its models, forms, urls and views (plus helpers,
reports, middleware, template tags, the import/export engine and the error pages):

```bash
cd seshat
python manage.py test
```

## 📥 Import & export

*Administration → Export* downloads items, categories, locations, customers, vendors and
their companies as CSV. *Administration → Import* reads the same format; download a
ready-made template for each module from the import page. Existing records are skipped,
and a file with an invalid row is rolled back entirely.

## ⬆️ Upgrading from SESHAT 1.x

Version 2 is a rewrite for Django 6.1 and Python 3.13. Field names were cleaned up
(`desciption` → `description`, `taxs_code` → `tax_code`), order lines were renamed
(`PurchaseItem`, `SaleItem`), and user activity now uses `x-django-app` instead of the old
`report` app. Start from a fresh database and bring your lists back in with the CSV
importer; JSON backups made by 1.x can't be restored directly.

## 🤝 Contributing

Issues and pull requests are welcome. Please keep the code style of the surrounding
code, add tests for new behavior, and make sure `python manage.py test` passes.

## 📄 License

SESHAT is released under the [MIT License](./LICENSE.md).
