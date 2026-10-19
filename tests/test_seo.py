import xml.etree.ElementTree as ET
from src.app import handle_request
from src.core.seo import INDEXNOW_KEY

def test_indexnow_key_route():
    event = {"rawPath": f"/{INDEXNOW_KEY}.txt", "headers": {"host": "backlotwire.com"}}
    res = handle_request(event)
    assert res["statusCode"] == 200
    assert res["headers"]["Content-Type"] == "text/plain; charset=utf-8"
    assert res["body"] == INDEXNOW_KEY

def test_rss_feed_route():
    event = {"rawPath": "/rss.xml", "headers": {"host": "backlotwire.com"}}
    res = handle_request(event)
    assert res["statusCode"] == 200
    assert "application/rss+xml" in res["headers"]["Content-Type"]
    assert "<rss version=\"2.0\"" in res["body"]
    assert "Backlot Wire" in res["body"]
    
    # Verify XML parses without error
    root = ET.fromstring(res["body"])
    assert root.tag == "rss"
    channel = root.find("channel")
    assert channel is not None
    assert channel.find("title").text.startswith("Backlot Wire")

def test_sitemap_xml_route():
    event = {"rawPath": "/sitemap.xml", "headers": {"host": "backlotwire.com"}}
    res = handle_request(event)
    assert res["statusCode"] == 200
    assert "application/xml" in res["headers"]["Content-Type"]
    assert "<urlset" in res["body"]
    root = ET.fromstring(res["body"])
    assert "urlset" in root.tag

def test_llms_txt_route():
    event = {"rawPath": "/llms.txt", "headers": {"host": "backlotwire.com"}}
    res = handle_request(event)
    assert res["statusCode"] == 200
    assert "text/markdown" in res["headers"]["Content-Type"]
    assert "Backlot Wire" in res["body"]
    assert "/rss.xml" in res["body"]

def test_robots_txt_route():
    event = {"rawPath": "/robots.txt", "headers": {"host": "backlotwire.com"}}
    res = handle_request(event)
    assert res["statusCode"] == 200
    assert "Sitemap: https://backlotwire.com/sitemap.xml" in res["body"]
    assert "LLMs-Txt: https://backlotwire.com/llms.txt" in res["body"]

def test_ssr_html_seo_tags():
    event = {"rawPath": "/", "headers": {"host": "backlotwire.com"}}
    res = handle_request(event)
    assert res["statusCode"] == 200
    body = res["body"]
    assert '<link rel="canonical" href="https://backlotwire.com/">' in body
    assert '<link rel="alternate" type="application/rss+xml"' in body
    assert '<meta property="og:site_name" content="Backlot Wire">' in body
    assert '<meta name="twitter:card" content="summary_large_image">' in body
    assert '"@type": "NewsMediaOrganization"' in body
    assert '"@type": "ItemList"' in body
