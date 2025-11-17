from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class AngelListScraper(Crawl4AIBaseScraper):
    """Scraper for AngelList (Wellfound) startup jobs"""
    
    def __init__(self):
        super().__init__(
            source_name="AngelList",
            base_url="https://wellfound.com",  # AngelList rebranded to Wellfound
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape startup job listings from AngelList/Wellfound
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters
        """
        try:
            # Wellfound jobs page
            url = f"{self.base_url}/jobs"
            
            keyword_str = ", ".join(keywords) if keywords else "startup and tech"
            instruction = f"""
            Extract startup job opportunities from this page.
            Focus on roles related to: {keyword_str}
            
            For each job listing, extract:
            - Job title/role
            - Startup/company name
            - Job description
            - Location or "Remote"
            - Direct URL to the job
            - Skills/tags required
            - Salary range or equity information if shown
            
            Only extract actual job postings, not company profiles or ads.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"AngelList: Skipping non-dict item: {type(opp)}")
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
            
            logger.info(f"AngelList: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping AngelList: {e}")
            return []
