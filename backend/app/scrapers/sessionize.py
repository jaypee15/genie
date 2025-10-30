from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class SessionizeScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="sessionize",
            base_url="https://sessionize.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/events"
            html = await self._fetch(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            opportunities = []
            
            event_items = soup.find_all('div', class_='event-item') or soup.find_all('article')
            
            for item in event_items[:20]:
                try:
                    title_elem = item.find('h3') or item.find('h2') or item.find('a')
                    title = title_elem.text.strip() if title_elem else "Unknown Event"
                    
                    link_elem = item.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    event_url = link_elem['href']
                    if not event_url.startswith('http'):
                        event_url = f"{self.base_url}{event_url}"
                    
                    description = ""
                    desc_elem = item.find('p')
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    location = "TBD"
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": title,
                            "description": description,
                            "url": event_url,
                            "location": location,
                            "remote": False,
                            "tags": ["speaking", "conference", "sessionize"]
                        },
                        opportunity_type="speaking"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing event item: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Sessionize")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Sessionize: {e}")
            return []

