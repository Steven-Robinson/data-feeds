# Data Feeds — Multi-Domain Live Intelligence Platform

A high-density, zero-fluff live intelligence engine supporting multiple specialized domains from a single codebase.

---

## 🏛️ Architecture Overview

```text
data-feeds/
├── cli.py                     # Command-line interface (sync, radar, serve)
├── requirements.txt           # Python dependencies
├── pytest.ini                 # Test configuration
├── config.example.env         # Environment template
├── src/
│   ├── app.py                 # Universal HTTP / AWS Lambda entrypoint
│   ├── core/                  # Shared data ingestion & processing engine
│   │   ├── models.py          # Standardized FeedItem, DomainConfig, ProductionStage
│   │   ├── rss_engine.py      # Resilient RSS parser with word-boundary exclusion filters
│   │   └── telemetry.py       # Real-human visitor evaluation & bot exclusion
│   └── domains/               # Domain-specific modules
│       ├── registry.py        # Hostname-to-domain resolver
│       ├── entertainment/     # Backlot Wire (Film & TV Production Radar)
│       │   ├── config.py      # Trade feed sources & styling
│       │   ├── tmdb.py        # TMDb API client + fallback mock catalog
│       │   ├── stage_classifier.py # Production stage regex detector
│       │   ├── service.py     # Aggregation & classification service
│       │   └── ui.py          # High-performance SSR HTML interface
│       ├── ai_models/         # [Ready for expansion] Open-Source Model Wire
│       └── biotech/           # [Ready for expansion] Clinical Trial Catalyst Wire
└── tests/
    └── test_entertainment.py  # Automated regression & classification tests
```

---

## 🎬 Domain 1: Backlot Wire (`backlotwire.com`)
*Film & Television Production Radar — Zero-Fluff Industry Intelligence*

- **The Problem It Solves**: Entertainment media (ScreenRant, Collider) is clogged with 2,000-word clickbait articles just to answer whether a show has been renewed, when filming begins, or who is in the cast.
- **The Core Feeds**: Aggregates directly from Hollywood's primary trades (*Deadline*, *Variety*, *The Hollywood Reporter*).
- **Automated Stage Classification**: Automatically tags every story into actionable production phases:
  - `GREENLIT` / `RENEWED`
  - `CASTING` / `PRE_PRODUCTION`
  - `FILMING NOW`
  - `POST_PRODUCTION`
  - `RELEASE SCHEDULED`
  - `CANCELED`
- **TMDb Integration**: Cross-references titles with The Movie Database (TMDb) for high-res posters, official synopsis, and release dates.
- **SSR & Bot-Exclusion Telemetry**: Lightweight server-rendered interface with zero client-side framework bloat and privacy-safe human visitor telemetry.

---

## 🚀 Quickstart

### 1. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. CLI Commands
```bash
# Sync latest Hollywood trade feeds and display classified items
python cli.py sync

# View production stage distribution breakdown
python cli.py radar

# Run local development server
python cli.py serve --port 8000
```

### 3. Open in Browser
Navigate to `http://localhost:8000` to preview **Backlot Wire**.

### 4. Run Automated Tests
```bash
pytest tests/
```

---

## 🌐 Multi-Domain Hosting Strategy
The single codebase resolves the incoming `Host` header to serve the correct domain:
- `backlotwire.com` $\rightarrow$ Film & TV Production Radar
- `modelwire.dev` $\rightarrow$ Open-Source AI Model Wire *(Next)*
- `biocatalyst.io` $\rightarrow$ FDA Clinical Trial Catalyst Wire *(Next)*

Deployable in a single AWS Lambda function behind CloudFront via OpenTofu/Terraform.
