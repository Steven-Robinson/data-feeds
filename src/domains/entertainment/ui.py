import json
from typing import List, Optional
from src.core.models import FeedItem, ProductionStage
from src.domains.entertainment.config import ENTERTAINMENT_CONFIG

STAGE_BADGES = {
    ProductionStage.GREENLIT: ("#10b981", "GREENLIT"),
    ProductionStage.RENEWED: ("#059669", "RENEWED"),
    ProductionStage.WRITING: ("#6366f1", "WRITING"),
    ProductionStage.PRE_PRODUCTION: ("#8b5cf6", "CASTING"),
    ProductionStage.FILMING: ("#f59e0b", "FILMING NOW"),
    ProductionStage.POST_PRODUCTION: ("#3b82f6", "POST-PROD"),
    ProductionStage.RELEASE_SCHEDULED: ("#06b6d4", "RELEASE SET"),
    ProductionStage.RELEASED: ("#14b8a6", "IN THEATERS / STREAMING"),
    ProductionStage.CANCELED: ("#ef4444", "CANCELED"),
}

def render_backlot_ui(
    items: List[FeedItem],
    current_stage: Optional[str] = None,
    stage_counts: Optional[dict] = None
) -> str:
    stage_counts = stage_counts or {}
    total_count = len(items)

    # Build stage pipeline buttons
    stages_to_show = [
        (None, "ALL INTEL", total_count),
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
        active_cls = "bg-amber-500 text-black font-semibold shadow-amber-500/20" if is_active else "bg-[#181C24] text-gray-300 hover:bg-[#222733]"
        href = f"?stage={st_val}" if st_val else "/"
        pipeline_html += f"""
        <a href="{href}" class="px-3.5 py-1.5 rounded-lg text-xs tracking-wider transition-all duration-150 flex items-center gap-1.5 border border-white/5 {active_cls}">
            <span>{label}</span>
            <span class="text-[10px] px-1.5 py-0.5 rounded-full bg-black/30 opacity-80">{count}</span>
        </a>
        """

    cards_html = ""
    for item in items:
        badge_color, badge_text = STAGE_BADGES.get(item.stage, ("#64748b", "TRADE REPORT"))
        img_block = ""
        if item.image_url:
            img_block = f"""
            <div class="hidden sm:block w-36 h-24 rounded-lg overflow-hidden flex-shrink-0 bg-neutral-900 border border-white/5">
                <img src="{item.image_url}" alt="{item.title}" class="w-full h-full object-cover" loading="lazy" />
            </div>
            """

        cards_html += f"""
        <article class="p-4 sm:p-5 rounded-xl bg-[#12151C] border border-white/5 hover:border-amber-500/30 transition-all duration-200 flex gap-4 items-start group">
            {img_block}
            <div class="flex-1 min-w-0">
                <div class="flex flex-wrap items-center gap-2 mb-2">
                    <span class="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase border border-white/10" style="background-color: {badge_color}22; color: {badge_color}; border-color: {badge_color}44;">
                        {badge_text}
                    </span>
                    <span class="text-xs text-amber-400/80 font-medium">{item.source}</span>
                    <span class="text-xs text-neutral-500">•</span>
                    <time class="text-xs text-neutral-400" datetime="{item.pub_date_iso}">{item.pub_date_iso[:10]}</time>
                </div>
                <h3 class="text-base sm:text-lg font-bold text-white group-hover:text-amber-300 transition-colors leading-snug mb-1.5">
                    <a href="{item.link}" target="_blank" rel="noopener noreferrer">
                        {item.title}
                    </a>
                </h3>
                <p class="text-xs sm:text-sm text-neutral-400 line-clamp-2 leading-relaxed mb-3">
                    {item.summary}
                </p>
                <div class="flex items-center gap-3 text-xs">
                    <a href="{item.link}" target="_blank" rel="noopener noreferrer" class="text-amber-400 hover:text-amber-300 font-medium inline-flex items-center gap-1">
                        Read Trade Coverage <span aria-hidden="true">&rarr;</span>
                    </a>
                </div>
            </div>
        </article>
        """

    schema_ld = {
        "@context": "https://schema.org",
        "@type": "NewsMediaOrganization",
        "name": "Backlot Wire",
        "url": "https://backlotwire.com",
        "description": "Zero-fluff film and television production intelligence and release radar."
    }

    return f"""<!DOCTYPE html>
<html lang="en" class="bg-[#090B0E] text-neutral-100 antialiased">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{ENTERTAINMENT_CONFIG.seo_title_template}</title>
    <meta name="description" content="{ENTERTAINMENT_CONFIG.seo_desc_template}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="application/ld+json">
        {json.dumps(schema_ld)}
    </script>
    <style>
        body {{ font-family: 'Inter', sans-serif; }}
        .brand-title {{ font-family: 'Cinzel', serif; letter-spacing: 0.15em; }}
    </style>
</head>
<body class="min-h-screen bg-[#090B0E] flex flex-col selection:bg-amber-500 selection:text-black">
    <!-- Top Navigation Wire Bar -->
    <header class="border-b border-white/10 bg-[#0C0E14]/80 backdrop-blur sticky top-0 z-50">
        <div class="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-400 to-amber-600 flex items-center justify-center font-black text-black text-sm shadow-lg shadow-amber-500/20">
                    BW
                </div>
                <div>
                    <h1 class="brand-title text-base sm:text-lg font-bold text-white leading-none">BACKLOT WIRE</h1>
                    <p class="text-[10px] text-amber-400/90 font-medium tracking-wider uppercase">Film & TV Production Radar</p>
                </div>
            </div>
            <div class="flex items-center gap-4 text-xs">
                <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    Live Trade Feeds
                </span>
            </div>
        </div>
    </header>

    <!-- Main Hero & Production Pipeline Bar -->
    <main class="flex-1 max-w-6xl mx-auto w-full px-4 py-6 sm:py-8">
        <div class="mb-8">
            <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-6">
                <div>
                    <h2 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Production Status & Greenlight Wire</h2>
                    <p class="text-sm text-neutral-400 mt-1">Verified Hollywood trade reports tracking movies & shows from script to premiere date.</p>
                </div>
                <div class="text-xs text-neutral-400 font-mono">
                    Tracking <strong>{total_count}</strong> active developments
                </div>
            </div>

            <!-- Pipeline Stages Filter Bar -->
            <div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
                {pipeline_html}
            </div>
        </div>

        <!-- Wire Cards Grid -->
        <div class="space-y-3">
            {cards_html if cards_html else '<div class="p-12 text-center text-neutral-500 rounded-xl bg-[#12151C] border border-white/5">No active developments matching this stage.</div>'}
        </div>
    </main>

    <footer class="border-t border-white/10 bg-[#0C0E14] py-8 text-center text-xs text-neutral-500">
        <div class="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p>&copy; 2026 Backlot Wire. Zero-fluff entertainment intelligence network.</p>
            <p>Source feeds: Deadline, Variety, The Hollywood Reporter.</p>
        </div>
    </footer>

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
