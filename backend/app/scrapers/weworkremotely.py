from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class WeWorkRemotelyScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="weworkremotely",
            base_url="https://weworkremotely.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            category = filters.get("category", "programming")
            url = f"{self.base_url}/categories/remote-{category}-jobs"
            
            instruction = """
            Extract all remote job listings.
            Focus on:
            - Job titles
            - Company names
            - Job descriptions
            - Job categories (Programming, Design, Marketing, etc.)
            - Salary information if available
            - Links to job postings
            - Time zones or location preferences if mentioned
            All jobs are remote, but note any specific region requirements.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "job")
                # Ensure remote flag is set
                normalized["remote"] = True
                normalized["location"] = normalized.get("location", "Remote")
                if normalized.get("source_url"):
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from WeWorkRemotely")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping WeWorkRemotely: {e}")
            return []
