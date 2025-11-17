from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class WeWorkRemotelyScraper(Crawl4AIBaseScraper):
    """Scraper for We Work Remotely job board"""
    
    def __init__(self):
        super().__init__(
            source_name="WeWorkRemotely",
            base_url="https://weworkremotely.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape remote job listings from We Work Remotely
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters
        """
        try:
            # Main categories page
            url = f"{self.base_url}/categories/remote-programming-jobs"
            
            keyword_str = ", ".join(keywords) if keywords else "all programming and tech"
            instruction = f"""
            Extract remote job opportunities from this page.
            Focus on jobs related to: {keyword_str}
            
            For each job listing, extract:
            - Job title
            - Company name
            - Brief job description
            - Location (usually "Anywhere" or specific timezone)
            - Direct URL to apply
            - Job category/tags
            - Salary range if mentioned
            
            Only extract actual job postings, ignore ads and navigation.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"WeWorkRemotely: Skipping non-dict item: {type(opp)}")
                    continue
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", "Remote"),
                    "url": opp.get("url", ""),
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"WeWorkRemotely: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping WeWorkRemotely: {e}")
            return []
