from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class RemoteOKScraper(Crawl4AIBaseScraper):
    """Scraper for RemoteOK job board"""
    
    def __init__(self):
        super().__init__(
            source_name="RemoteOK",
            base_url="https://remoteok.com",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape remote job listings from RemoteOK
        
        Args:
            keywords: List of keywords to filter jobs
            filters: Additional filters (location, remote, etc.)
        """
        try:
            # RemoteOK main page has all recent jobs
            url = f"{self.base_url}/remote-jobs"
            
            # Build custom instruction based on keywords
            keyword_str = ", ".join(keywords) if keywords else "all types"
            instruction = f"""
            Extract remote job opportunities from this page.
            Focus on jobs related to: {keyword_str}
            
            For each job listing, extract:
            - Job title
            - Company name
            - Brief description
            - Location (should be "Remote" or specific location)
            - Direct URL to the job posting
            - Tags/skills (e.g., Python, React, etc.)
            - Salary/compensation if mentioned
            
            Only extract actual job listings, not ads or navigation elements.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"RemoteOK: Skipping non-dict item: {type(opp)}")
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
            
            logger.info(f"RemoteOK: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
            return []
