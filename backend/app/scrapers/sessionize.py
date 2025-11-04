from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class SessionizeScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="sessionize",
            base_url="https://sessionize.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/cfps"
            
            instruction = """
            Extract all open Call for Papers (CFPs) and speaking events.
            Focus on:
            - Event names
            - Event organizers or hosts
            - Event descriptions
            - Event locations (city, country, or online/virtual)
            - CFP submission deadlines
            - Links to event details or CFP submission pages
            Only include events with open CFPs, ignore closed or past events.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "speaking")
                if normalized.get("source_url"):
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Sessionize")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Sessionize: {e}")
            return []
