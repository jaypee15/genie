from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class PapercallScraper(Crawl4AIBaseScraper):
    """Scraper for Papercall.io speaking opportunities"""
    
    def __init__(self):
        super().__init__(
            source_name="Papercall",
            base_url="https://www.papercall.io",
            rate_limit=2
        )
    
    async def scrape(self, keywords: List[str] = None, **filters) -> List[Dict[str, Any]]:
        """
        Scrape speaking opportunities from Papercall.io
        
        Args:
            keywords: List of keywords/topics to filter
            filters: Additional filters
        """
        try:
            # Papercall events page
            url = f"{self.base_url}/events"
            
            keyword_str = ", ".join(keywords) if keywords else "tech and software"
            instruction = f"""
            Extract conference speaking opportunities (Call for Papers/CFPs) from this page.
            Focus on events related to: {keyword_str}
            
            For each CFP/event, extract:
            - Conference/event name
            - Organizer or conference name
            - Brief description of the event
            - Location (city/country or "Virtual")
            - Direct URL to the CFP
            - Topics/tags (e.g., DevOps, AI, Web Development)
            - Deadline or event date if mentioned
            
            Only extract actual CFP listings, not ads or navigation.
            """
            
            opportunities = await self._crawl_with_llm(url, instruction)
            
            # Normalize the data
            normalized = []
            for opp in opportunities:
                if not isinstance(opp, dict):
                    logger.warning(f"Papercall: Skipping non-dict item: {type(opp)}")
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
                    "opportunity_type": "speaking"
                })
            
            logger.info(f"Papercall: Found {len(normalized)} opportunities")
            return normalized
            
        except Exception as e:
            logger.error(f"Error scraping Papercall: {e}")
            return []
