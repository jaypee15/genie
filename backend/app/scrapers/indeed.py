from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)


class IndeedScraper(Crawl4AIBaseScraper):
    """Scraper for Indeed job board"""
    
    def __init__(self):
        super().__init__(
            source_name="Indeed",
            base_url="https://www.indeed.com",
            rate_limit=1  # Be more conservative with Indeed
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape job listings from Indeed
        
        Args:
            keywords: List of keywords to search for
            filters: Additional filters (location, remote, etc.)
        """
        try:
            # Build search query
            query = " ".join(keywords) if keywords else "software engineer"
            location = filters.get("location", "Remote")
            
            # Indeed search URL
            url = f"{self.base_url}/jobs?q={quote_plus(query)}&l={quote_plus(location)}"
            
            instruction = f"""
            Extract job opportunities from this Indeed search results page.
            Search query: {query}
            Location: {location}
            
            For each job listing, extract:
            - Job title
            - Company name
            - Job description summary
            - Location
            - Direct URL to the job posting (full Indeed URL)
            - Job type/tags if available
            - Salary information if displayed
            
            Only extract actual job listings from the search results.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Indeed: Skipping non-dict item: {type(opp)}")
                    continue
                # Ensure URLs are complete
                job_url = opp.get("url", "")
                if job_url and not job_url.startswith("http"):
                    job_url = f"{self.base_url}{job_url}"
                
                normalized.append({
                    "title": opp.get("title", ""),
                    "company": opp.get("company_or_organizer", ""),
                    "description": opp.get("description", ""),
                    "location": opp.get("location", location),
                    "url": job_url,
                    "tags": opp.get("tags", []),
                    "compensation": opp.get("compensation_info"),
                    "source": self.source_name,
                    "opportunity_type": "job"
                })
            
            logger.info(f"Indeed: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
            return []
