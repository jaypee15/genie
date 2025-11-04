from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class EventbriteScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="eventbrite",
            base_url="https://www.eventbrite.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            keywords = filters.get("keywords", ["tech", "startup", "developer"])
            location = filters.get("location", "online")
            
            query = "+".join(keywords) if isinstance(keywords, list) else keywords
            url = f"{self.base_url}/d/{location}/{query}--events"
            
            instruction = """
            Extract all upcoming events.
            Focus on:
            - Event names/titles
            - Event organizers
            - Brief event descriptions
            - Event locations or "Online"
            - Event dates
            - Links to event pages
            - Ticket prices if visible (Free, Paid, price range)
            Only include future events, ignore past events.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "event")
                if normalized.get("source_url"):
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Eventbrite")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Eventbrite: {e}")
            return []
