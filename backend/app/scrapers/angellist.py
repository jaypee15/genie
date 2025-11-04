from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class AngelListScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="angellist",
            base_url="https://wellfound.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            role = filters.get("role", "software-engineer")
            url = f"{self.base_url}/role/r/{role}"
            
            instruction = """
            Extract all startup job opportunities.
            Focus on:
            - Job titles/roles
            - Startup/company names
            - Job descriptions
            - Locations (or Remote)
            - Salary ranges or equity compensation
            - Links to job applications
            - Company stage (Seed, Series A, etc.) if visible
            - Tags like "Early Employee", "Founding Team", etc.
            Only include active job postings.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "job")
                if normalized.get("source_url"):
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from AngelList/Wellfound")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping AngelList: {e}")
            return []
