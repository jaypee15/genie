import pytest
from app.scrapers.base import BaseScraper
from app.scrapers import get_scrapers_for_goal_type, get_all_scrapers


def test_get_scrapers_for_job_type():
    scrapers = get_scrapers_for_goal_type("job")
    assert len(scrapers) > 0
    assert all(isinstance(s, BaseScraper) for s in scrapers)


def test_get_scrapers_for_speaking_type():
    scrapers = get_scrapers_for_goal_type("speaking")
    assert len(scrapers) > 0
    assert all(isinstance(s, BaseScraper) for s in scrapers)


def test_get_all_scrapers():
    scrapers = get_all_scrapers()
    assert len(scrapers) >= 8
    assert all(isinstance(s, BaseScraper) for s in scrapers)


@pytest.mark.asyncio
async def test_base_scraper_rate_limiting():
    class TestScraper(BaseScraper):
        def __init__(self):
            super().__init__("test", "https://example.com", rate_limit=1)
        
        async def scrape(self, filters):
            return []
    
    scraper = TestScraper()
    assert scraper.rate_limit == 1
    assert scraper.source_name == "test"

