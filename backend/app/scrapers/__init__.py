"""
Scrapers package.

This package now uses Tavily for web search + generic Crawl4AI extraction
instead of hard-coded per-site template scrapers.

The ExecutorAgent handles the Tavily search and extraction flow.
"""
from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper

# Empty registry - we no longer use template-specific scrapers
SCRAPER_REGISTRY: Dict[str, Crawl4AIBaseScraper] = {}

# Empty goal type mapping - Tavily handles discovery for all goal types
GOAL_TYPE_TO_SCRAPERS = {
    "speaking": [],
    "job": [],
    "event": [],
    "grant": [],
}


def get_scrapers_for_goal_type(goal_type: str) -> List[Crawl4AIBaseScraper]:
    """
    Returns scrapers for a given goal type.
    Now returns empty list as Tavily + generic Crawl4AI handles all discovery.
    """
    return []


def get_all_scrapers() -> List[Crawl4AIBaseScraper]:
    """Returns all registered scrapers (now empty)."""
    return []


def get_scraper(name: str) -> Crawl4AIBaseScraper:
    """Get a scraper by name (now returns None)."""
    return None


__all__ = [
    "Crawl4AIBaseScraper",
    "get_scrapers_for_goal_type",
    "get_all_scrapers",
    "get_scraper",
    "SCRAPER_REGISTRY"
]
