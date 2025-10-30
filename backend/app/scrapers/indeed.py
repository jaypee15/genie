from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="indeed",
            base_url="https://www.indeed.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            keywords = filters.get("keywords", ["software engineer"])
            query = "+".join(keywords) if isinstance(keywords, list) else "software+engineer"
            
            url = f"{self.base_url}/jobs?q={query}&l=Remote"
            html = await self._fetch(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            opportunities = []
            
            job_cards = soup.find_all('div', class_='job_seen_beacon') or soup.find_all('a', class_='jcs-JobTitle')
            
            for card in job_cards[:15]:
                try:
                    link = card.find('a', href=True)
                    if not link:
                        link = card if card.name == 'a' else None
                    
                    if not link:
                        continue
                    
                    job_url = link['href']
                    if not job_url.startswith('http'):
                        job_url = f"{self.base_url}{job_url}"
                    
                    title = link.text.strip() if link.text else "Unknown Position"
                    
                    company_elem = card.find('span', class_='companyName')
                    company = company_elem.text.strip() if company_elem else "Unknown Company"
                    
                    location_elem = card.find('div', class_='companyLocation')
                    location = location_elem.text.strip() if location_elem else "Remote"
                    
                    snippet_elem = card.find('div', class_='job-snippet')
                    description = snippet_elem.text.strip() if snippet_elem else ""
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": f"{title} at {company}",
                            "description": description,
                            "url": job_url,
                            "location": location,
                            "remote": "remote" in location.lower(),
                            "tags": ["indeed", "job"]
                        },
                        opportunity_type="job"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Indeed")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Indeed: {e}")
            return []

