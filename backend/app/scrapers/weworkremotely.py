from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class WeWorkRemotelyScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="weworkremotely",
            base_url="https://weworkremotely.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/categories/remote-programming-jobs"
            html = await self._fetch(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            opportunities = []
            
            job_listings = soup.find_all('li', class_='feature')
            
            for listing in job_listings[:20]:
                try:
                    link = listing.find('a', href=True)
                    if not link:
                        continue
                    
                    job_url = link['href']
                    if not job_url.startswith('http'):
                        job_url = f"{self.base_url}{job_url}"
                    
                    title_elem = listing.find('span', class_='title')
                    title = title_elem.text.strip() if title_elem else "Unknown Position"
                    
                    company_elem = listing.find('span', class_='company')
                    company = company_elem.text.strip() if company_elem else "Unknown Company"
                    
                    category_elem = listing.find('span', class_='region')
                    category = category_elem.text.strip() if category_elem else ""
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": f"{title} at {company}",
                            "description": category,
                            "url": job_url,
                            "location": "Remote",
                            "remote": True,
                            "tags": ["remote", "programming"]
                        },
                        opportunity_type="job"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job listing: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from WeWorkRemotely")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping WeWorkRemotely: {e}")
            return []

