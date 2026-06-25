# Real Estate AI Platform

An AI-powered real estate management platform combining **ML property valuation**, **investment scoring**, **neighborhood analysis**, and a full **software licensing system** — all served through a FastAPI REST API.

## Features

- 🏠 **AI Property Valuation** — Gradient Boosting model predicting sale prices with confidence intervals
- 📊 **Investment Scoring** — Cap rate, gross yield, and liquidity-based scoring (0–100)
- 🗺️ **Neighborhood Intelligence** — Composite scoring across schools, safety, walkability, amenities
- 🔍 **Comparative Market Analysis (CMA)** — Benchmark against comparable sold properties
- 🔑 **License Management** — Issue, validate, revoke, and renew platform licenses (Basic/Pro/Enterprise)
- 🚀 **FastAPI REST API** with Swagger UI at `/docs`

## Architecture

```
┌──────────────────────────────────────────────┐
│           Real Estate AI Platform            │
│                                              │
│  /properties/*      /licenses/*             │
│       │                   │                 │
│  ┌────┴────┐        ┌─────┴──────┐          │
│  │ ML Layer│        │  License   │          │
│  │  • GBM  │        │  Manager   │          │
│  │  • CBF  │        │  • Issue   │          │
│  │  • CMA  │        │  • Validate│          │
│  └─────────┘        └────────────┘          │
└──────────────────────────────────────────────┘
```

## Quick Start

```bash
git clone https://github.com/AlaaDarwish282/real-estate-ai-platform.git
cd real-estate-ai-platform
pip install -r requirements.txt
python main.py
```

API docs: `http://localhost:8003/docs`

## Example API Calls

```bash
# Valuate a property
curl -X POST http://localhost:8003/api/v1/properties/valuate \
  -H "Content-Type: application/json" \
  -d '{"area_sqft": 2000, "bedrooms": 3, "bathrooms": 2, "year_built": 2010, "distance_to_center_km": 5}'

# Issue a license
curl -X POST http://localhost:8003/api/v1/licenses/issue \
  -H "Content-Type: application/json" \
  -d '{"owner_email": "user@example.com", "license_type": "professional", "organization": "Acme Realty"}'

# Validate a license
curl http://localhost:8003/api/v1/licenses/validate/RE-PROFESSIONAL-XXXX

# Score an investment
curl -X POST http://localhost:8003/api/v1/properties/investment-score \
  -H "Content-Type: application/json" \
  -d '{"price": 350000, "annual_rent_estimate": 24000, "days_on_market": 30}'
```

## License Types

| Type | Duration | API Calls/Day | Users | Properties |
|------|----------|---------------|-------|------------|
| Basic | 30 days | 100 | 1 | 50 |
| Professional | 1 year | 5,000 | 10 | 500 |
| Enterprise | 2 years | Unlimited | Unlimited | Unlimited |

## License

MIT
