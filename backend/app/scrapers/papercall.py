from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class PapercallScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="papercall",
            base_url="https://www.papercall.io"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/events"
            
            instruction = """
            Extract all Call for Proposals (CFP) and speaking opportunities.
            Focus on:
            - Conference or event names
            - Event organizers
            - Speaking opportunity descriptions
            - Event locations
            - CFP submission deadlines if visible
            - Links to detailed event pages
            Ignore past events or closed CFPs.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "speaking")
                if normalized.get("source_url"):
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Papercall")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Papercall: {e}")
            return []
