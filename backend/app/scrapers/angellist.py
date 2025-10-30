from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class AngelListScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="angellist",
            base_url="https://wellfound.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/jobs"
            html = await self._fetch(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            opportunities = []
            
            job_cards = soup.find_all('div', class_='job-card') or soup.find_all('div', attrs={'data-test': 'JobSearchCard'})
            
            for card in job_cards[:20]:
                try:
                    link = card.find('a', href=True)
                    if not link:
                        continue
                    
                    job_url = link['href']
                    if not job_url.startswith('http'):
                        job_url = f"{self.base_url}{job_url}"
                    
                    title_elem = card.find('h2') or card.find('h3')
                    title = title_elem.text.strip() if title_elem else "Unknown Position"
                    
                    company_elem = card.find(class_='company-name') or card.find('span', class_='name')
                    company = company_elem.text.strip() if company_elem else "Startup"
                    
                    location = "Remote"
                    location_elem = card.find(class_='location')
                    if location_elem:
                        location = location_elem.text.strip()
                    
                    description = ""
                    desc_elem = card.find('p')
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": f"{title} at {company}",
                            "description": description,
                            "url": job_url,
                            "location": location,
                            "remote": "remote" in location.lower(),
                            "tags": ["startup", "angellist"]
                        },
                        opportunity_type="job"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from AngelList")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping AngelList: {e}")
            return []

