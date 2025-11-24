from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
from app.scrapers.papercall import PapercallScraper
from app.scrapers.sessionize import SessionizeScraper
from app.scrapers.remoteok import RemoteOKScraper
from app.scrapers.weworkremotely import WeWorkRemotelyScraper
from app.scrapers.indeed import IndeedScraper
from app.scrapers.ycjobs import YCJobsScraper
from app.scrapers.wellfound import WellFoundScraper
from app.scrapers.eventbrite import EventbriteScraper

SCRAPER_REGISTRY: Dict[str, Crawl4AIBaseScraper] = {
    "papercall": PapercallScraper(),
    "sessionize": SessionizeScraper(),
    "remoteok": RemoteOKScraper(),
    "weworkremotely": WeWorkRemotelyScraper(),
    "indeed": IndeedScraper(),
    "ycombinator": YCJobsScraper(),
    "wellfound": WellFoundScraper(),
    "eventbrite": EventbriteScraper(),
}

GOAL_TYPE_TO_SCRAPERS = {
    "speaking": ["papercall", "sessionize", "eventbrite"],
    "job": ["remoteok", "weworkremotely", "indeed", "ycombinator", "wellfound"],
    "event": ["eventbrite", "papercall"],
    "grant": [],
}


def get_scrapers_for_goal_type(goal_type: str) -> List[Crawl4AIBaseScraper]:
    scraper_names = GOAL_TYPE_TO_SCRAPERS.get(goal_type, [])
    return [SCRAPER_REGISTRY[name] for name in scraper_names if name in SCRAPER_REGISTRY]


def get_all_scrapers() -> List[Crawl4AIBaseScraper]:
    return list(SCRAPER_REGISTRY.values())


def get_scraper(name: str) -> Crawl4AIBaseScraper:
    return SCRAPER_REGISTRY.get(name)


__all__ = [
    "Crawl4AIBaseScraper",
    "get_scrapers_for_goal_type",
    "get_all_scrapers",
    "get_scraper",
    "SCRAPER_REGISTRY"
]