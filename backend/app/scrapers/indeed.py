from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class IndeedScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="indeed",
            base_url="https://www.indeed.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            job_title = filters.get("job_title", "software developer")
            location = filters.get("location", "")
            
            url = f"{self.base_url}/jobs?q={job_title}&l={location}"
            
            instruction = """
            Extract all job listings from the search results.
            Focus on:
            - Job titles/positions
            - Company names
            - Job descriptions or summaries
            - Job locations (city, state, or Remote)
            - Salary information if shown
            - Links to job detail pages
            - Job types (Full-time, Part-time, Contract, etc.)
            Only extract actual job listings, ignore ads or promoted content markers.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "job")
                if normalized.get("source_url"):
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Indeed")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
            return []
