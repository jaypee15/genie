from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class YCJobsScraper(Crawl4AIBaseScraper):
    """Scraper for Y Combinator Jobs board"""
    
    def __init__(self):
        super().__init__(
            source_name="YC Jobs",
            base_url="https://www.ycombinator.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape job listings from Y Combinator Jobs
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters
        """
        try:
            # YC Jobs page
            url = f"{self.base_url}/jobs"
            
            keyword_str = ", ".join(keywords) if keywords else "startup and engineering"
            instruction = f"""
            Extract job opportunities from Y Combinator companies.
            Focus on roles related to: {keyword_str}
            
            For each job listing, extract:
            - Job title
            - Company name (YC-backed startup)
            - Job description
            - Location or "Remote"
            - Direct URL to apply
            - Required skills/technologies
            - Salary or equity information if mentioned
            
            Only extract actual job listings from YC companies.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"YC Jobs: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", ""),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"YC Jobs: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping YC Jobs: {e}")
            return []

