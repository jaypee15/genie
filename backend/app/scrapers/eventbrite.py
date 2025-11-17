from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)


class EventbriteScraper(Crawl4AIBaseScraper):
    """Scraper for Eventbrite events and conferences"""
    
    def __init__(self):
        super().__init__(
            source_name="Eventbrite",
            base_url="https://www.eventbrite.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape events and conferences from Eventbrite
        
        Args:
            keywords: List of keywords to search for
            filters: Additional filters
        """
        try:
            # Build search query
            query = " ".join(keywords) if keywords else "tech conference"
            location = filters.get("location", "online")
            
            # Eventbrite search URL
            url = f"{self.base_url}/d/{quote_plus(location)}/{quote_plus(query)}/"
            
            instruction = f"""
            Extract tech events, conferences, and meetups from this page.
            Search query: {query}
            Location: {location}
            
            For each event, extract:
            - Event name/title
            - Organizer name
            - Event description
            - Location (city or "Online Event")
            - Direct URL to the event page
            - Event category/tags
            - Ticket price or "Free" if mentioned
            
            Only extract actual event listings, not ads or promotions.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Eventbrite: Skipping non-dict item: {type(opp)}")
                    continue
                # Ensure URLs are complete
                event_url = opp.get("url", "")
                if event_url and not event_url.startswith("http"):
                    event_url = f"{self.base_url}{event_url}"
                
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", location),
                    "url": event_url,
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "event"
                })
            
            logger.info(f"Eventbrite: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping Eventbrite: {e}")
            return []
