import json
from typing import List, Optional
from src.core.models import FeedItem, ProductionStage
from src.domains.entertainment.config import ENTERTAINMENT_CONFIG, STUDIOS_CONFIG

STAGE_BADGES = {
    ProductionStage.GREENLIT: ("#f59e0b", "#000000", "GREENLIT"),
    ProductionStage.RENEWED: ("#10b981", "#000000", "RENEWED"),
    ProductionStage.WRITING: ("#818cf8", "#ffffff", "WRITERS ROOM"),
    ProductionStage.PRE_PRODUCTION: ("#c084fc", "#000000", "CASTING / PRE-PROD"),
    ProductionStage.FILMING: ("#ef4444", "#ffffff", "FILMING ON SET"),
    ProductionStage.POST_PRODUCTION: ("#38bdf8", "#000000", "POST-PRODUCTION"),
    ProductionStage.RELEASE_SCHEDULED: ("#34d399", "#000000", "RELEASE SLATED"),
    ProductionStage.RELEASED: ("#94a3b8", "#000000", "IN THEATERS"),
    ProductionStage.CANCELED: ("#dc2626", "#ffffff", "CANCELED / SHELVED"),
}

def render_backlot_ui(
    items: List[FeedItem],
    current_stage: Optional[str] = None,
    current_studio: Optional[str] = None,
    stage_counts: Optional[dict] = None,
    all_items: Optional[List[FeedItem]] = None,
    base_url: str = "https://backlotwire.com"
) -> str:
    stage_counts = stage_counts or {}
    total_count = len(items)
    base_url = base_url.rstrip("/")

    # Build canonical URL
    params = []
    if current_stage:
        params.append(f"stage={current_stage}")
    if current_studio:
        params.append(f"studio={current_studio}")
    query_str = f"?{'&'.join(params)}" if params else ""
    canonical_url = f"{base_url}/{query_str}"

    # Stages for the filter switchboard
    stages_to_show = [
        (None, "ALL DESKS", total_count),
        (ProductionStage.GREENLIT.value, "GREENLIT", stage_counts.get("GREENLIT", 0) + stage_counts.get("RENEWED", 0)),
        (ProductionStage.PRE_PRODUCTION.value, "CASTING", stage_counts.get("PRE_PRODUCTION", 0)),
        (ProductionStage.FILMING.value, "FILMING", stage_counts.get("FILMING", 0)),
        (ProductionStage.POST_PRODUCTION.value, "POST-PROD", stage_counts.get("POST_PRODUCTION", 0)),
        (ProductionStage.RELEASE_SCHEDULED.value, "RELEASE DATES", stage_counts.get("RELEASE_SCHEDULED", 0)),
        (ProductionStage.CANCELED.value, "CANCELED", stage_counts.get("CANCELED", 0)),
    ]

    pipeline_html = ""
    for st_val, label, count in stages_to_show:
        is_active = (current_stage == st_val) or (current_stage is None and st_val is None)
        active_cls = "stage-btn-active" if is_active else "stage-btn-inactive"
        p = []
        if st_val:
            p.append(f"stage={st_val}")
        if current_studio:
            p.append(f"studio={current_studio}")
        href = f"?{'&'.join(p)}" if p else "/"
        pipeline_html += f"""
        <a href="{href}" class="stage-switch-btn {active_cls}">
            <span class="stage-name">{label}</span>
            <span class="stage-count">[{count}]</span>
        </a>
        """

    # Separate lead story from remaining wire items
    lead_story = items[0] if items else None
    wire_items = items[1:] if len(items) > 1 else []

    lead_html = ""
    if lead_story:
        bg_col, fg_col, badge_text = STAGE_BADGES.get(lead_story.stage, ("#f59e0b", "#000000", "TRADE REPORT"))
        lead_img_url = lead_story.image_url or "/assets/default-article.jpg"
        lead_img = f"""
        <div class="lead-thumb-wrap">
            <img src="{lead_img_url}" alt="{lead_story.title}" class="lead-thumb" loading="eager" />
        </div>
        """
        lead_html = f"""
        <article class="lead-article-card">
            <div class="lead-meta-bar">
                <span class="stage-tag" style="background-color: {bg_col}; color: {fg_col};">
                    {badge_text}
                </span>
                <span class="lead-source">{lead_story.source.upper()}</span>
                <span class="sep">/</span>
                <span class="lead-dateline">WIRE PRIORITY DISPATCH</span>
                <span class="sep">/</span>
                <time class="lead-time">{lead_story.pub_date_iso[:10]}</time>
            </div>
            {lead_img}
            <div class="lead-body">
                <h3 class="lead-title">
                    <a href="{lead_story.link}" target="_blank" rel="noopener noreferrer">
                        {lead_story.title}
                    </a>
                </h3>
                <p class="lead-summary">
                    {lead_story.summary}
                </p>
                <div class="lead-footer">
                    <a href="{lead_story.link}" target="_blank" rel="noopener noreferrer" class="read-trade-link">
                        READ ORIGINAL TRADE DISPATCH <span class="arrow">&rarr;</span>
                    </a>
                </div>
            </div>
        </article>
        """

    # Wire stories list
    wire_rows_html = ""
    for item in wire_items:
        bg_col, fg_col, badge_text = STAGE_BADGES.get(item.stage, ("#64748b", "#ffffff", "TRADE REPORT"))
        thumb_url = item.image_url or "/assets/default-article.jpg"
        thumb_markup = f"""
        <div class="row-thumb-wrap">
            <img src="{thumb_url}" alt="{item.title}" class="row-thumb" loading="lazy" />
        </div>
        """

        wire_rows_html += f"""
        <article class="wire-row">
            {thumb_markup}
            <div class="wire-content">
                <div class="wire-meta-line">
                    <span class="stage-tag-sm" style="border-color: {bg_col}; color: {bg_col};">
                        [{badge_text}]
                    </span>
                    <span class="wire-source-name">{item.source.upper()}</span>
                    <span class="sep">/</span>
                    <time class="wire-date">{item.pub_date_iso[:10]}</time>
                </div>
                <h4 class="wire-headline">
                    <a href="{item.link}" target="_blank" rel="noopener noreferrer">
                        {item.title}
                    </a>
                </h4>
                <p class="wire-snippet">
                    {item.summary}
                </p>
                <div class="wire-action">
                    <a href="{item.link}" target="_blank" rel="noopener noreferrer" class="wire-link">
                        Trade Coverage &rarr;
                    </a>
                </div>
            </div>
        </article>
        """

    # 1. Studio Lot Activity Index
    source_for_counts = all_items if all_items is not None else items

    studio_counts = []
    max_studio_count = 1
    for s in STUDIOS_CONFIG:
        cnt = sum(1 for it in source_for_counts if any(kw in (it.title + " " + it.summary).lower() for kw in s["keywords"]))
        if cnt > 0:
            studio_counts.append((s, cnt))
            if cnt > max_studio_count:
                max_studio_count = cnt

    if not studio_counts:
        for s in STUDIOS_CONFIG[:5]:
            studio_counts.append((s, 2))
        max_studio_count = 2

    # Active studio details
    active_studio_obj = next((s for s in STUDIOS_CONFIG if s["slug"] == current_studio), None) if current_studio else None
    active_studio_name = active_studio_obj["name"] if active_studio_obj else (current_studio.upper() if current_studio else None)

    studio_meter_html = ""
    for s, cnt in sorted(studio_counts, key=lambda x: x[1], reverse=True)[:8]:
        pct = max(14, int((cnt / max_studio_count) * 100))
        is_active = (current_studio == s["slug"])
        active_cls = " active-studio" if is_active else ""
        count_badge = f"[{cnt} ACTIVE]" if not is_active else f"[{cnt} SELECTED &times;]"

        # Toggle URL: if active, clicking clears studio filter; if inactive, sets it
        p = []
        if current_stage:
            p.append(f"stage={current_stage}")
        if not is_active:
            p.append(f"studio={s['slug']}")
        href = f"?{'&'.join(p)}" if p else "/"

        studio_meter_html += f"""
        <a href="{href}" class="studio-meter-link{active_cls}" title="Filter intelligence wire by {s['name']}">
            <div class="studio-header">
                <span class="studio-name">{s['name']}</span>
                <span class="studio-count">{count_badge}</span>
            </div>
            <div class="studio-bar-bg">
                <div class="studio-bar-fill" style="width: {pct}%;"></div>
            </div>
        </a>
        """

    # Active studio banner in main column
    active_studio_banner_html = ""
    if current_studio:
        p = []
        if current_stage:
            p.append(f"stage={current_stage}")
        reset_studio_href = f"?{'&'.join(p)}" if p else "/"
        active_studio_banner_html = f"""
        <div class="active-studio-banner">
            <div class="active-studio-info">
                <span class="active-studio-tag">[STUDIO LOT FILTER]</span>
                <span class="active-studio-name">{active_studio_name.upper()}</span>
                <span class="active-studio-count">({total_count} {'dispatch' if total_count == 1 else 'dispatches'})</span>
            </div>
            <a href="{reset_studio_href}" class="active-studio-clear" title="Clear studio filter">&times; SHOW ALL STUDIOS</a>
        </div>
        """

    if current_stage and current_studio:
        desk_heading = f"DESK: {current_stage} // {active_studio_name.upper()}"
    elif current_stage:
        desk_heading = f"DESK: {current_stage}"
    elif current_studio:
        desk_heading = f"STUDIO LOT: {active_studio_name.upper()}"
    else:
        desk_heading = "ACTIVE PRODUCTION DESK"

    # 2. Release & Festival Radar (Items with dates/premieres/releases)
    release_candidates = [
        it for it in items
        if (it.stage == ProductionStage.RELEASE_SCHEDULED or
            any(w in (it.title + " " + it.summary).lower() for w in ("release", "premieres", "theatrical", "slated", "festival", "gala"))
        )
    ][:3]

    release_radar_html = ""
    for it in release_candidates:
        release_radar_html += f"""
        <div class="radar-card">
            <div class="radar-tag">[DATE RADAR] // {it.source.upper()}</div>
            <a href="{it.link}" target="_blank" rel="noopener noreferrer" class="radar-title">
                {it.title}
            </a>
            <div class="radar-date">{it.pub_date_iso[:10]}</div>
        </div>
        """

    schema_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "NewsMediaOrganization",
                "name": "Backlot Wire",
                "url": base_url,
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{base_url}/assets/mark.jpg"
                },
                "description": "Zero-fluff film and television production intelligence and release radar."
            },
            {
                "@type": "ItemList",
                "name": "Active Production Radar Dispatches",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i + 1,
                        "item": {
                            "@type": "NewsArticle",
                            "headline": it.title,
                            "url": it.link,
                            "datePublished": it.pub_date_iso,
                            "description": it.summary,
                            "publisher": {
                                "@type": "Organization",
                                "name": it.source
                            }
                        }
                    }
                    for i, it in enumerate(items[:10])
                ]
            }
        ]
    }

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ENTERTAINMENT_CONFIG.seo_title_template}</title>
    <meta name="description" content="{ENTERTAINMENT_CONFIG.seo_desc_template}">
    <link rel="canonical" href="{canonical_url}">
    <link rel="alternate" type="application/rss+xml" title="Backlot Wire RSS Feed" href="{base_url}/rss.xml">
    
    <!-- OpenGraph Meta Tags -->
    <meta property="og:site_name" content="Backlot Wire">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{ENTERTAINMENT_CONFIG.seo_title_template}">
    <meta property="og:description" content="{ENTERTAINMENT_CONFIG.seo_desc_template}">
    <meta property="og:url" content="{canonical_url}">
    <meta property="og:image" content="{base_url}/assets/alley.jpg">
    <meta property="og:image:width" content="1400">
    <meta property="og:image:height" content="800">

    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{ENTERTAINMENT_CONFIG.seo_title_template}">
    <meta name="twitter:description" content="{ENTERTAINMENT_CONFIG.seo_desc_template}">
    <meta name="twitter:image" content="{base_url}/assets/alley.jpg">

    <link rel="icon" type="image/jpeg" href="/assets/mark.jpg">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,500;0,6..72,700;1,6..72,400&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script type="application/ld+json">
        {json.dumps(schema_ld)}
    </script>
    <style>
        :root {{
            --bg-canvas: #0c0e12;
            --bg-panel: #12141a;
            --bg-elevated: #181b22;
            --border-hairline: #242731;
            --border-strong: #363a47;
            --amber-kodak: #f59e0b;
            --amber-warm: #d97706;
            --beacon-red: #ef4444;
            --text-heading: #f3efe6;
            --text-body: #c7cbd4;
            --text-muted: #727885;
            --font-brand: 'Cinzel', serif;
            --font-headline: 'Newsreader', serif;
            --font-mono: 'IBM Plex Mono', monospace;
            --font-sans: 'Inter', -apple-system, sans-serif;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-canvas);
            color: var(--text-body);
            font-family: var(--font-sans);
            font-size: 15px;
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
        }}

        a {{ color: inherit; text-decoration: none; }}

        /* Top Broadsheet Masthead */
        .masthead {{
            background-color: #090a0d;
            border-top: 4px solid var(--amber-kodak);
            border-bottom: 1px solid var(--border-hairline);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .masthead-inner {{
            max-width: 1240px;
            margin: 0 auto;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}
        .brand-block {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .brand-mark-frame {{
            width: 44px;
            height: 44px;
            background: #151820;
            border: 1px solid var(--border-strong);
            border-radius: 4px;
            overflow: hidden;
            flex-shrink: 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.4);
        }}
        .brand-mark-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .brand-titles {{
            display: flex;
            flex-direction: column;
        }}
        .brand-name {{
            font-family: var(--font-brand);
            font-size: 20px;
            font-weight: 800;
            letter-spacing: 0.16em;
            color: #ffffff;
            line-height: 1;
        }}
        .brand-tagline {{
            font-family: var(--font-mono);
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.12em;
            color: var(--amber-kodak);
            text-transform: uppercase;
            margin-top: 4px;
        }}

        /* Lot Clocks (Burbank / London / NY) */
        .lot-clocks {{
            display: none;
            align-items: center;
            gap: 16px;
            font-family: var(--font-mono);
            font-size: 11px;
            color: var(--text-muted);
            border-left: 1px solid var(--border-hairline);
            padding-left: 18px;
        }}
        @media (min-width: 860px) {{
            .lot-clocks {{ display: flex; }}
        }}
        .clock-item strong {{
            color: #d1d5db;
            font-weight: 600;
        }}
        .live-stage-beacon {{
            display: flex;
            align-items: center;
            gap: 7px;
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 600;
            color: #fca5a5;
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 4px 10px;
            border-radius: 2px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}
        .beacon-dot {{
            width: 7px;
            height: 7px;
            background: var(--beacon-red);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--beacon-red);
            display: inline-block;
        }}

        /* Hero Soundstage Alley Banner */
        .hero-banner {{
            position: relative;
            background-color: #0b0c10;
            background-image:
                linear-gradient(180deg, rgba(8,10,14,0.30) 0%, rgba(8,10,14,0.10) 45%, rgba(8,10,14,0.85) 100%),
                url('/assets/alley.jpg');
            background-size: cover;
            background-position: center 36%;
            border-bottom: 2px solid var(--border-strong);
            padding: 64px 20px 52px 20px;
        }}
        .hero-inner {{
            max-width: 1240px;
            margin: 0 auto;
        }}
        .hero-slate {{
            display: inline-block;
            max-width: 820px;
            background: rgba(11, 13, 17, 0.82);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-left: 4px solid var(--amber-kodak);
            border-top: 1px solid rgba(255,255,255,0.12);
            border-right: 1px solid rgba(255,255,255,0.08);
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding: 24px 30px;
            border-radius: 2px;
            box-shadow: 0 16px 40px rgba(0,0,0,0.65);
        }}
        .soundstage-stamped-label {{
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 600;
            color: var(--amber-kodak);
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .hero-headline {{
            font-family: var(--font-brand);
            font-size: clamp(24px, 4vw, 36px);
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 0.04em;
            line-height: 1.15;
            max-width: 820px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.8);
        }}
        .hero-deck {{
            font-family: var(--font-sans);
            font-size: clamp(13px, 1.8vw, 15px);
            color: #b3b9c6;
            max-width: 720px;
            margin-top: 10px;
            line-height: 1.6;
        }}
        .hero-spec-strip {{
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.1);
            font-family: var(--font-mono);
            font-size: 11px;
            color: #9ba1b0;
        }}
        .spec-item strong {{
            color: #e5e7eb;
        }}

        /* Switchboard Stage Filter Bar */
        .stage-switchboard-wrap {{
            background: #0f1116;
            border-bottom: 1px solid var(--border-hairline);
            padding: 12px 20px;
        }}
        .stage-switchboard {{
            max-width: 1240px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            gap: 8px;
            overflow-x: auto;
            scrollbar-width: thin;
        }}
        .stage-switch-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 12px;
            border-radius: 2px;
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            white-space: nowrap;
            transition: all 0.15s ease;
        }}
        .stage-btn-active {{
            background: var(--amber-kodak);
            color: #000000;
            border: 1px solid var(--amber-kodak);
            box-shadow: 0 1px 4px rgba(245, 158, 11, 0.3);
        }}
        .stage-btn-inactive {{
            background: #14171e;
            color: #8c92a0;
            border: 1px solid var(--border-hairline);
        }}
        .stage-btn-inactive:hover {{
            background: #1a1e27;
            color: #e2e5ec;
            border-color: var(--border-strong);
        }}
        .stage-count {{
            font-size: 10px;
            opacity: 0.85;
        }}

        /* Main Multi-Desk Layout */
        .main-container {{
            max-width: 1240px;
            margin: 0 auto;
            padding: 28px 20px 48px 20px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 32px;
        }}
        @media (min-width: 980px) {{
            .main-container {{
                grid-template-columns: 1fr 340px;
            }}
        }}

        /* Section Headings */
        .desk-header {{
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--border-strong);
            margin-bottom: 20px;
        }}
        .desk-title {{
            font-family: var(--font-mono);
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: var(--text-heading);
            text-transform: uppercase;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .desk-title::before {{
            content: '';
            display: inline-block;
            width: 4px;
            height: 12px;
            background: var(--amber-kodak);
        }}
        .desk-meta {{
            font-family: var(--font-mono);
            font-size: 11px;
            color: var(--text-muted);
        }}

        /* Lead Article Card */
        .lead-article-card {{
            background: var(--bg-panel);
            border: 1px solid var(--border-hairline);
            border-radius: 4px;
            padding: 24px;
            margin-bottom: 28px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        }}
        .lead-meta-bar {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            margin-bottom: 14px;
            font-family: var(--font-mono);
            font-size: 11px;
        }}
        .stage-tag {{
            font-size: 10px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 2px;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .lead-source {{
            color: var(--amber-kodak);
            font-weight: 600;
        }}
        .sep {{
            color: #3b404d;
        }}
        .lead-dateline {{
            color: #8c92a0;
        }}
        .lead-time {{
            color: #5c6270;
        }}
        .lead-thumb-wrap {{
            width: 100%;
            max-height: 380px;
            overflow: hidden;
            border-radius: 2px;
            border: 1px solid var(--border-hairline);
            margin-bottom: 18px;
            background: #000;
        }}
        .lead-thumb {{
            width: 100%;
            height: 100%;
            max-height: 380px;
            object-fit: cover;
            display: block;
        }}
        .lead-title {{
            font-family: var(--font-headline);
            font-size: clamp(22px, 3vw, 30px);
            font-weight: 700;
            color: #ffffff;
            line-height: 1.25;
            margin-bottom: 12px;
        }}
        .lead-title a:hover {{
            color: var(--amber-kodak);
        }}
        .lead-summary {{
            font-size: 15px;
            color: var(--text-body);
            line-height: 1.6;
            margin-bottom: 18px;
        }}
        .lead-footer {{
            padding-top: 12px;
            border-top: 1px solid var(--border-hairline);
        }}
        .read-trade-link {{
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 600;
            color: var(--amber-kodak);
            letter-spacing: 0.08em;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .read-trade-link:hover {{
            color: #fbbf24;
            text-decoration: underline;
        }}

        /* Wire Rows List */
        .wire-stream {{
            display: flex;
            flex-direction: column;
            border-top: 1px solid var(--border-hairline);
        }}
        .wire-row {{
            display: flex;
            gap: 18px;
            padding: 20px 0;
            border-bottom: 1px solid var(--border-hairline);
            align-items: flex-start;
        }}
        .wire-row:hover .wire-headline a {{
            color: var(--amber-kodak);
        }}
        .row-thumb-wrap {{
            width: 130px;
            height: 86px;
            border-radius: 2px;
            border: 1px solid var(--border-hairline);
            overflow: hidden;
            background: #000;
            flex-shrink: 0;
        }}
        @media (max-width: 580px) {{
            .row-thumb-wrap {{ display: none; }}
        }}
        .row-thumb {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }}
        .wire-content {{
            flex: 1;
            min-width: 0;
        }}
        .wire-meta-line {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            font-family: var(--font-mono);
            font-size: 11px;
            margin-bottom: 6px;
        }}
        .stage-tag-sm {{
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            border: 1px solid;
            padding: 1px 6px;
            border-radius: 2px;
        }}
        .wire-source-name {{
            color: #d1d5db;
            font-weight: 600;
        }}
        .wire-date {{
            color: #606775;
        }}
        .wire-headline {{
            font-family: var(--font-headline);
            font-size: 19px;
            font-weight: 700;
            color: var(--text-heading);
            line-height: 1.35;
            margin-bottom: 6px;
        }}
        .wire-snippet {{
            font-size: 13px;
            color: #8c93a0;
            line-height: 1.5;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 10px;
        }}
        .wire-action {{
            font-family: var(--font-mono);
            font-size: 11px;
        }}
        .wire-link {{
            color: var(--amber-kodak);
            font-weight: 500;
        }}
        .wire-link:hover {{
            text-decoration: underline;
        }}

        /* Sidebar: Studio Lot Index, Release Radar & Syndication Desk */
        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        .sidebar-panel {{
            background: var(--bg-panel);
            border: 1px solid var(--border-hairline);
            border-radius: 4px;
            padding: 18px;
        }}
        .panel-heading {{
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.12em;
            color: #ffffff;
            text-transform: uppercase;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border-hairline);
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        /* Active Studio Filter Banner */
        .active-studio-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            background: rgba(245, 158, 11, 0.08);
            border-left: 3px solid var(--amber-kodak);
            border-top: 1px solid rgba(245, 158, 11, 0.2);
            border-right: 1px solid rgba(245, 158, 11, 0.1);
            border-bottom: 1px solid rgba(245, 158, 11, 0.1);
            padding: 10px 14px;
            border-radius: 2px;
            margin-bottom: 24px;
            font-family: var(--font-mono);
        }}
        .active-studio-info {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            font-size: 11px;
        }}
        .active-studio-tag {{
            color: #9ca3af;
            letter-spacing: 0.08em;
        }}
        .active-studio-name {{
            color: #ffffff;
            font-weight: 700;
            letter-spacing: 0.06em;
            background: rgba(245, 158, 11, 0.2);
            padding: 2px 7px;
            border-radius: 2px;
            border: 1px solid rgba(245, 158, 11, 0.35);
        }}
        .active-studio-count {{
            color: #9ca3af;
            font-size: 11px;
        }}
        .active-studio-clear {{
            color: #fca5a5;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.06em;
            text-decoration: none;
            padding: 4px 8px;
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 2px;
            white-space: nowrap;
            transition: all 0.15s;
        }}
        .active-studio-clear:hover {{
            background: rgba(239, 68, 68, 0.25);
            color: #ffffff;
            border-color: rgba(239, 68, 68, 0.5);
        }}

        /* Studio Lot Index */
        .studio-meter-list {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .studio-meter-link {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding: 8px 10px;
            margin: 0 -10px;
            border-radius: 3px;
            border: 1px solid transparent;
            text-decoration: none;
            color: inherit;
            transition: all 0.15s ease;
        }}
        .studio-meter-link:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.12);
        }}
        .studio-meter-link.active-studio {{
            background: rgba(245, 158, 11, 0.12);
            border-color: rgba(245, 158, 11, 0.45);
        }}
        .studio-meter-link.active-studio .studio-name {{
            color: var(--amber-kodak);
            font-weight: 700;
        }}
        .studio-meter-link.active-studio .studio-bar-fill {{
            background: var(--amber-kodak);
            box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
        }}
        .studio-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
        }}
        .studio-name {{
            color: #d1d5db;
            font-weight: 500;
            transition: color 0.15s;
        }}
        .studio-count {{
            font-family: var(--font-mono);
            font-size: 10px;
            color: var(--amber-kodak);
            font-weight: 600;
        }}
        .studio-bar-bg {{
            width: 100%;
            height: 4px;
            background: #1e222b;
            border-radius: 2px;
            overflow: hidden;
        }}
        .studio-bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--amber-warm), var(--amber-kodak));
            border-radius: 2px;
        }}

        /* Release Radar */
        .radar-card-list {{
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .radar-card {{
            padding-bottom: 10px;
            border-bottom: 1px dotted rgba(255,255,255,0.08);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .radar-card:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}
        .radar-tag {{
            font-family: var(--font-mono);
            font-size: 10px;
            color: var(--amber-kodak);
            font-weight: 600;
        }}
        .radar-title {{
            font-size: 13px;
            font-weight: 500;
            color: #d1d5db;
            line-height: 1.4;
        }}
        .radar-title:hover {{
            color: var(--amber-kodak);
        }}
        .radar-date {{
            font-family: var(--font-mono);
            font-size: 10px;
            color: #6b7280;
        }}

        /* Syndication Desk */
        .syndication-desk {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .feed-copy-box {{
            display: flex;
            align-items: center;
            background: #090a0d;
            border: 1px solid var(--border-hairline);
            border-radius: 2px;
            padding: 4px 6px;
            gap: 6px;
        }}
        .feed-url-text {{
            font-family: var(--font-mono);
            font-size: 10px;
            color: #9ca3af;
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .btn-copy-feed {{
            background: var(--amber-kodak);
            color: #000;
            font-family: var(--font-mono);
            font-size: 10px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 2px;
            border: none;
            cursor: pointer;
            transition: opacity 0.15s;
            flex-shrink: 0;
        }}
        .btn-copy-feed:hover {{ opacity: 0.9; }}
        .syndication-links {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}
        .synd-link-badge {{
            font-family: var(--font-mono);
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 2px;
            background: #181b23;
            border: 1px solid var(--border-hairline);
            color: #9da3af;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .synd-link-badge:hover {{
            color: #fff;
            border-color: var(--amber-kodak);
        }}

        /* Methodology Box */
        .method-text {{
            font-size: 12px;
            color: #8c93a0;
            line-height: 1.6;
        }}
        .method-text p + p {{
            margin-top: 10px;
        }}
        .trade-badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 12px;
        }}
        .trade-pill {{
            font-family: var(--font-mono);
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 2px;
            background: #191c24;
            border: 1px solid var(--border-hairline);
            color: #9da3af;
        }}

        /* Footer */
        .footer {{
            border-top: 1px solid var(--border-hairline);
            background: #08090c;
            padding: 32px 20px;
            font-family: var(--font-mono);
            font-size: 11px;
            color: #606775;
        }}
        .footer-inner {{
            max-width: 1240px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            align-items: center;
            text-align: center;
        }}
        @media (min-width: 680px) {{
            .footer-inner {{
                flex-direction: row;
                justify-content: space-between;
                text-align: left;
            }}
        }}
        .footer-brand {{
            color: #9ca3af;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <!-- Top Broadsheet Masthead -->
    <header class="masthead">
        <div class="masthead-inner">
            <div class="brand-block">
                <div class="brand-mark-frame">
                    <img src="/assets/mark.jpg" alt="Backlot Wire Water Tower Mark" class="brand-mark-img">
                </div>
                <div class="brand-titles">
                    <a href="/" class="brand-name">BACKLOT WIRE</a>
                    <span class="brand-tagline">Film & TV Production Intelligence // Trade Wire</span>
                </div>
            </div>

            <!-- Studio Time Zones -->
            <div class="lot-clocks">
                <div class="clock-item">BURBANK: <strong id="clock-burbank">--:-- PT</strong></div>
                <div class="clock-item">LEAVESDEN: <strong id="clock-london">--:-- BST</strong></div>
                <div class="clock-item">MANHATTAN: <strong id="clock-ny">--:-- ET</strong></div>
            </div>

            <div class="live-stage-beacon">
                <span class="beacon-dot"></span>
                <span>STAGE HOT</span>
            </div>
        </div>
    </header>

    <!-- Soundstage Alley Hero Banner -->
    <section class="hero-banner">
        <div class="hero-inner">
            <div class="hero-slate">
                <div class="soundstage-stamped-label">
                    <span>SOUNDSTAGE 24</span>
                    <span>//</span>
                    <span>GLOBAL PRODUCTION MONITOR</span>
                </div>
                <h1 class="hero-headline">Hollywood Greenlight & Production Radar</h1>
                <p class="hero-deck">
                    Aggregated, verified trade intelligence tracking major studio features, network commissions, and streaming orders through every phase of physical production.
                </p>
                <div class="hero-spec-strip">
                    <div class="spec-item">ACTIVE DEVELOPMENTS: <strong>{total_count}</strong></div>
                    <div class="spec-item">PRIMARY TRADES: <strong>DEADLINE • VARIETY • THR</strong></div>
                    <div class="spec-item">COVERAGE LATENCY: <strong>SUB-10M REAL-TIME</strong></div>
                </div>
            </div>
        </div>
    </section>

    <!-- Stage Filter Switchboard -->
    <nav class="stage-switchboard-wrap" aria-label="Production Stage Filter">
        <div class="stage-switchboard">
            {pipeline_html}
        </div>
    </nav>

    <!-- Main Editorial Layout -->
    <main class="main-container">
        <!-- Main Column: Lead Story & Wire Stream -->
        <section>
            <div class="desk-header">
                <h2 class="desk-title">{desk_heading}</h2>
                <span class="desk-meta">SHOWING {total_count} ITEMS</span>
            </div>

            {active_studio_banner_html}

            {lead_html}

            <div class="wire-stream">
                {wire_rows_html if wire_rows_html else '<div style="padding: 40px; text-align: center; color: #606775; font-family: var(--font-mono); font-size: 12px;">NO ADDITIONAL TRADE DISPATCHES RECORDED FOR THIS STAGE.</div>'}
            </div>
        </section>

        <!-- Sidebar: Studio Lot Index, Release Radar & Syndication Desk -->
        <aside class="sidebar">
            <!-- Studio Production Index -->
            <div class="sidebar-panel">
                <div class="panel-heading">
                    <span>STUDIO LOT INDEX</span>
                    <span style="color: var(--amber-kodak); font-size: 10px;">[ACTIVE SLATE]</span>
                </div>
                <div class="studio-meter-list">
                    {studio_meter_html}
                </div>
            </div>

            <!-- Release Radar -->
            <div class="sidebar-panel">
                <div class="panel-heading">
                    <span>UPCOMING RELEASE RADAR</span>
                    <span style="color: var(--amber-kodak); font-size: 10px;">[DATES]</span>
                </div>
                <div class="radar-card-list">
                    {release_radar_html if release_radar_html else '<div style="font-size: 11px; color: #6b7280; font-family: var(--font-mono);">NO LOCKED DATES IN ACTIVE BUFFER.</div>'}
                </div>
            </div>

            <!-- Syndication & Developer Desk -->
            <div class="sidebar-panel">
                <div class="panel-heading">
                    <span>SYNDICATION &amp; DEVELOPER DESK</span>
                </div>
                <div class="syndication-desk">
                    <div class="feed-copy-box">
                        <span class="feed-url-text" id="rss-url-text">{base_url}/rss.xml</span>
                        <button class="btn-copy-feed" id="btn-copy-rss" onclick="copyFeedUrl()">COPY RSS</button>
                    </div>
                    <div class="syndication-links">
                        <a href="/rss.xml" target="_blank" class="synd-link-badge">RSS 2.0</a>
                        <a href="/api/feed" target="_blank" class="synd-link-badge">JSON API</a>
                        <a href="/sitemap.xml" target="_blank" class="synd-link-badge">SITEMAP</a>
                        <a href="/llms.txt" target="_blank" class="synd-link-badge">LLMS.TXT</a>
                    </div>
                </div>
            </div>

            <!-- Verification Protocol -->
            <div class="sidebar-panel">
                <div class="panel-heading">
                    <span>VERIFICATION PROTOCOL</span>
                </div>
                <div class="method-text">
                    <p>
                        <strong>Zero editorial fluff.</strong> Every item is parsed directly from verified industry trades with automated stage classification and talent attachment extraction.
                    </p>
                    <p>
                        Direct RSS ingestion with GDPR-compliant privacy telemetry. No cookies or tracker scripts.
                    </p>
                </div>
                <div class="trade-badges">
                    <span class="trade-pill">DEADLINE</span>
                    <span class="trade-pill">VARIETY</span>
                    <span class="trade-pill">HOLLYWOOD REPORTER</span>
                    <span class="trade-pill">TMDB VERIFIED</span>
                </div>
            </div>
        </aside>
    </main>

    <!-- Broadsheet Footer -->
    <footer class="footer">
        <div class="footer-inner">
            <div>
                <span class="footer-brand">BACKLOT WIRE</span> &mdash; Hollywood Production Intelligence Network.
            </div>
            <div>
                Syndicated from verified industry trade bureaus.
            </div>
        </div>
    </footer>

    <!-- Studio Clocks Script -->
    <script>
        function updateClocks() {{
            const now = new Date();
            const formatTime = (tz) => {{
                try {{
                    return new Intl.DateTimeFormat('en-GB', {{
                        timeZone: tz,
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    }}).format(now);
                }} catch(e) {{
                    return '--:--';
                }}
            }};
            const pt = formatTime('America/Los_Angeles');
            const bst = formatTime('Europe/London');
            const et = formatTime('America/New_York');

            const elBurbank = document.getElementById('clock-burbank');
            const elLondon = document.getElementById('clock-london');
            const elNy = document.getElementById('clock-ny');

            if (elBurbank) elBurbank.textContent = pt + ' PT';
            if (elLondon) elLondon.textContent = bst + ' BST';
            if (elNy) elNy.textContent = et + ' ET';
        }}
        updateClocks();
        setInterval(updateClocks, 30000);

        function copyFeedUrl() {{
            const textEl = document.getElementById('rss-url-text');
            const url = textEl ? textEl.textContent.trim() : (window.location.origin + '/rss.xml');
            navigator.clipboard.writeText(url).then(() => {{
                const btn = document.getElementById('btn-copy-rss');
                if (btn) {{
                    const orig = btn.textContent;
                    btn.textContent = 'COPIED!';
                    setTimeout(() => {{ btn.textContent = orig; }}, 2000);
                }}
            }}).catch(() => {{}});
        }}
    </script>

    <!-- Client Telemetry Script (Bot Excluded) -->
    <script>
        (function() {{
            try {{
                const sid = 's_' + Math.random().toString(36).substring(2, 18);
                const payload = {{
                    sid: sid,
                    path: window.location.pathname + window.location.search,
                    ref: document.referrer || '',
                    screen: screen.width + 'x' + screen.height,
                    lang: navigator.language || '',
                    wd: Boolean(navigator.webdriver)
                }};
                navigator.sendBeacon('/api/telemetry', JSON.stringify(payload));
            }} catch(e) {{}}
        }})();
    </script>
</body>
</html>
"""
