import pytest
from src.core.models import ProductionStage
from src.domains.entertainment.stage_classifier import classify_stage, extract_title_candidate
from src.domains.entertainment.tmdb import TMDbClient
from src.domains.registry import registry
from src.app import handle_request

def test_stage_classification():
    # Greenlit
    assert classify_stage("HBO Greenlights Game of Thrones Spinoff Series") == ProductionStage.GREENLIT
    # Filming
    assert classify_stage("The Batman Part II Begins Filming in London Next Month") == ProductionStage.FILMING
    # Casting / Pre-production
    assert classify_stage("Pedro Pascal Joins Cast of Upcoming Sci-Fi Thriller") == ProductionStage.PRE_PRODUCTION
    # Post-production
    assert classify_stage("Stranger Things Season 5 Wraps Production Ahead of 2026 Release") == ProductionStage.POST_PRODUCTION
    # Canceled
    assert classify_stage("Netflix Has Canceled Mystery Drama After One Season") == ProductionStage.CANCELED

def test_extract_title_candidate():
    assert extract_title_candidate("‘Stranger Things’ Season 5 Begins Filming") == "Stranger Things"
    assert extract_title_candidate('"Euphoria" Season 3 Sets Production Date') == "Euphoria"

def test_tmdb_mock_fallback():
    client = TMDbClient(api_key=None)
    results = client.search_multi("Stranger Things")
    assert len(results) > 0
    assert "Stranger Things" in results[0]["title"]

def test_domain_registry_routing():
    assert registry.resolve_domain("backlotwire.com") == "entertainment"
    assert registry.resolve_domain("www.backlotwire.com") == "entertainment"
    assert registry.resolve_domain("unknown-domain.com") == "entertainment"

def test_handle_request_home():
    res = handle_request({"rawPath": "/", "headers": {"host": "backlotwire.com"}})
    assert res["statusCode"] == 200
    assert "BACKLOT WIRE" in res["body"]

def test_handle_request_telemetry():
    res = handle_request({
        "rawPath": "/api/telemetry",
        "httpMethod": "POST",
        "headers": {"host": "backlotwire.com", "user-agent": "Mozilla/5.0"},
        "body": '{"path": "/", "screen": "1920x1080"}'
    })
    assert res["statusCode"] == 204

def test_studio_lot_ui_and_filtering():
    # 1. Base home page should have clickable studio meter links
    res_home = handle_request({"rawPath": "/", "headers": {"host": "backlotwire.com"}})
    assert res_home["statusCode"] == 200
    assert "studio-meter-link" in res_home["body"]
    assert "?studio=" in res_home["body"]

    # 2. Filtered by studio=netflix
    res_studio = handle_request({
        "rawPath": "/",
        "queryStringParameters": {"studio": "netflix"},
        "headers": {"host": "backlotwire.com"}
    })
    assert res_studio["statusCode"] == 200
    assert "STUDIO LOT FILTER" in res_studio["body"]
    assert "active-studio" in res_studio["body"]
    assert "SHOW ALL STUDIOS" in res_studio["body"]

def test_api_feed_studio_filtering():
    import json
    res = handle_request({
        "rawPath": "/api/feed",
        "queryStringParameters": {"studio": "netflix"},
        "headers": {"host": "backlotwire.com"}
    })
    assert res["statusCode"] == 200
    items = json.loads(res["body"])
    assert isinstance(items, list)
    # Every item returned should contain netflix keywords
    for it in items:
        text = (it["title"] + " " + it["summary"]).lower()
        assert "netflix" in text
