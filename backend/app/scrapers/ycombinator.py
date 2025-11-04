from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class YCombinatorScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="ycombinator",
            base_url="https://www.ycombinator.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/jobs"
            
            instruction = """
            Extract all YC startup job postings.
            Focus on:
            - Job titles/positions
            - Company names (YC-backed startups)
            - Job descriptions
            - Locations or Remote status
            - Salary ranges and equity if shown
            - Links to job details or application pages
            - YC batch information if visible
            Only include open positions from YC companies.
            """
            
            raw_opportunities = await self._crawl_with_llm(url, instruction)
            
            opportunities = []
            for raw_opp in raw_opportunities:
                normalized = self._normalize_opportunity(raw_opp, "job")
                if normalized.get("source_url"):
                    # Add YC-specific metadata
                    normalized["tags"] = normalized.get("tags", []) + ["ycombinator", "startup"]
                    opportunities.append(normalized)
            
            logger.info(f"Scraped {len(opportunities)} opportunities from YCombinator")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping YCombinator: {e}")
            return []
