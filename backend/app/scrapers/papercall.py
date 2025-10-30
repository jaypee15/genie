from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class PapercallScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="papercall",
            base_url="https://www.papercall.io"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/events"
            html = await self._fetch(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            opportunities = []
            
            event_cards = soup.find_all('div', class_='event-card')
            
            for card in event_cards[:20]:
                try:
                    title_elem = card.find('h3') or card.find('h2')
                    title = title_elem.text.strip() if title_elem else "Unknown Event"
                    
                    link_elem = card.find('a', href=True)
                    if not link_elem:
                        continue
                    
                    event_url = link_elem['href']
                    if not event_url.startswith('http'):
                        event_url = f"{self.base_url}{event_url}"
                    
                    description_elem = card.find('p')
                    description = description_elem.text.strip() if description_elem else ""
                    
                    location = "Unknown"
                    location_elem = card.find(class_='location')
                    if location_elem:
                        location = location_elem.text.strip()
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": title,
                            "description": description,
                            "url": event_url,
                            "location": location,
                            "remote": "virtual" in location.lower() or "online" in location.lower(),
                            "tags": ["speaking", "conference", "cfp"]
                        },
                        opportunity_type="speaking"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing event card: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Papercall")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Papercall: {e}")
            return []

