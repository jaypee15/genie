import pytest
from app.scrapers.papercall import PapercallScraper


@pytest.mark.asyncio
async def test_papercall_normalization_skips_invalid_items(monkeypatch):
    scraper = PapercallScraper()
    # Mixed valid dict and invalid string item
    fake_results = [
        {"title": "Conf A", "company_or_organizer": "Org", "url": "https://example.com"},
        "not-a-dict",
    ]
    monkeypatch.setattr(scraper, "_crawl_with_llm", lambda url, instruction=None: fake_results)
    items = await scraper.scrape(keywords=["python"])
    assert len(items) == 1
    assert items[0]["title"] == "Conf A"
    assert items[0]["opportunity_type"] == "speaking"


