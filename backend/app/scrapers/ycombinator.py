from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class YCombinatorScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="ycombinator",
            base_url="https://www.ycombinator.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/jobs"
            html = await self._fetch(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            opportunities = []
            
            job_items = soup.find_all('div', class_='job') or soup.find_all('a', class_='job-link')
            
            for item in job_items[:20]:
                try:
                    link = item.find('a', href=True)
                    if not link:
                        link = item if item.name == 'a' else None
                    
                    if not link:
                        continue
                    
                    job_url = link['href']
                    if not job_url.startswith('http'):
                        job_url = f"{self.base_url}{job_url}"
                    
                    title_elem = item.find('h3') or item.find('h2') or link
                    title = title_elem.text.strip() if title_elem else "Unknown Position"
                    
                    company_elem = item.find(class_='company-name')
                    company = company_elem.text.strip() if company_elem else "YC Startup"
                    
                    location = "Various"
                    location_elem = item.find(class_='location')
                    if location_elem:
                        location = location_elem.text.strip()
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": f"{title} at {company}",
                            "description": "Y Combinator startup position",
                            "url": job_url,
                            "location": location,
                            "remote": "remote" in location.lower(),
                            "tags": ["yc", "startup", "job"]
                        },
                        opportunity_type="job"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job item: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from YCombinator")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping YCombinator: {e}")
            return []

