# ShopEase — E-Commerce Website + Admin Dashboard

A Flask, SQLite, HTML, CSS and JavaScript student project. The original product catalogue, search, product details and JSON APIs are retained and extended with an admin dashboard.

## Added features

- **Admin login:** session-protected admin pages and analytics/CSS APIs.
- **User analytics:** unique browser visitors, active visitors (last 5 minutes), total page views, country count, country-wise visitor table and a seven-day traffic chart.
- **Real visitor tracking:** the storefront records a random browser identifier and page path. It does not collect a name or email address. Country lookup is best-effort through `ipapi.co`; private/local IP addresses are not sent to the geolocation provider. If the lookup fails, the country is `Unknown`.
- **Traffic simulator:** creates 1–5,000 clearly marked sample visitors across selected countries. Simulated data is kept separate from real visitors and can be selected in analytics.
- **CSS generator:** color, font, padding, border radius and shadow controls, live preview, generated CSS, copy and save functionality.
- **Saved styles:** CSS snippets are stored in SQLite. Saving a snippet does not automatically change the storefront theme.

## Requirements

- Python 3.10+
- pip
- Internet connection only if you want public-IP country lookup or the existing external sample product images

## Run on Windows (Command Prompt)

1. Extract the ZIP and open Command Prompt in `ecommerce_part1`.
2. Create and activate a virtual environment:
   ```bat
   py -m venv .venv
   .venv\Scripts\activate.bat
   ```
3. Install dependencies:
   ```bat
   python -m pip install -r requirements.txt
   ```
4. Initialize the database (this preserves an existing products table and adds the new tables):
   ```bat
   python init_db.py
   ```
5. Set your own admin credentials and a long secret key before starting the server:
   ```bat
   set ADMIN_USERNAME=admin
   set ADMIN_PASSWORD=Choose-A-Strong-Password
   set FLASK_SECRET_KEY=replace-this-with-a-long-random-secret
   python app.py
   ```
6. Open the storefront at `http://127.0.0.1:5000`.
7. Open the admin login at `http://127.0.0.1:5000/admin/login`.

The development fallback login is `admin` / `admin12345` if environment variables are not set. **Change it before sharing or deploying the project.** The fallback Flask secret key is also development-only. Do not expose Flask's development server to the public internet.

## Run on Linux / WSL / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python init_db.py
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD='Choose-A-Strong-Password'
export FLASK_SECRET_KEY='replace-this-with-a-long-random-secret'
python app.py
```

Then visit `http://127.0.0.1:5000` and `http://127.0.0.1:5000/admin/login`.

## Admin dashboard guide

1. Sign in at `/admin/login`.
2. **User analytics:** overview cards show real users, active users, identified countries and real visits. The country table can switch between real and simulated visitors. Traffic can show all, real or simulated page views.
3. **Traffic simulator:** enter a count from 1 to 5,000, choose one or more countries (Ctrl-click to select multiple), and click **Run simulation**. It creates test data immediately; it is not a real bot or a background traffic generator.
4. **CSS generator:** change controls and see the preview update. Copy the generated CSS or save it under a name. Saved CSS is a reusable snippet and is not automatically injected into the live storefront.

## Analytics and privacy notes

- A browser's local storage keeps a random visitor ID so repeat visits from that browser count as one unique visitor. Clearing browser storage or using another browser/device creates a new visitor ID.
- Country is inferred from the request IP address. localhost/private IP visits show as `Local / Unknown`; public-IP geolocation depends on the external provider, network access and provider limits. Do not interpret unknown country as a failed visitor.
- The app uses `request.remote_addr` and does not trust arbitrary forwarded-IP headers. If deployed behind a reverse proxy, configure proxy handling carefully before enabling accurate geolocation.
- This is a learning/demo analytics implementation, not a consent-management or production analytics platform. Add an appropriate privacy notice/consent process for your deployment and review local privacy requirements.
- Simulated visitors are flagged in the database (`is_simulated=1`) and excluded from real-user totals.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/products` | List/search products |
| GET | `/api/products/<id>` | Product details |
| POST | `/api/track` | Record a storefront page view |
| GET | `/api/analytics/overview` | Admin analytics summary |
| GET | `/api/analytics/countries?source=real` | Country-wise unique visitor counts (`real` or `simulated`) |
| GET | `/api/analytics/traffic?source=all` | Daily page views (`all`, `real` or `simulated`) |
| POST | `/api/simulator/run` | Create sample visitor records (admin only) |
| GET | `/api/css/saved` | List saved CSS snippets (admin only) |
| POST | `/api/css/save` | Save generated CSS (admin only) |

Admin APIs require a logged-in admin session. The database is `products.db`, created by `init_db.py`. Existing product records are not deleted by the new initialization.

## Project structure

```text
ecommerce_part1/
├── app.py
├── init_db.py
├── schema.sql
├── requirements.txt
├── README.md
├── products.db                 # generated when initialized
├── templates/
│   ├── index.html
│   ├── admin_login.html
│   ├── admin.html
│   └── css_generator.html
└── static/
    ├── style.css
    ├── app.js
    ├── tracking.js
    ├── admin.css
    ├── admin.js
    └── css-generator.js
```
