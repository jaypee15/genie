from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class EventbriteScraper(BaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="eventbrite",
            base_url="https://www.eventbrite.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            keywords = filters.get("keywords", ["tech", "conference"])
            query = "+".join(keywords) if isinstance(keywords, list) else "tech"
            
            url = f"{self.base_url}/d/online/tech-events/"
            html = await self._fetch(url)
            
            soup = BeautifulSoup(html, 'lxml')
            
            opportunities = []
            
            event_cards = soup.find_all('div', class_='event-card') or soup.find_all('article')
            
            for card in event_cards[:20]:
                try:
                    link = card.find('a', href=True)
                    if not link:
                        continue
                    
                    event_url = link['href']
                    if not event_url.startswith('http'):
                        event_url = f"{self.base_url}{event_url}"
                    
                    title_elem = card.find('h3') or card.find('h2') or link
                    title = title_elem.text.strip() if title_elem else "Unknown Event"
                    
                    description = ""
                    desc_elem = card.find('p')
                    if desc_elem:
                        description = desc_elem.text.strip()
                    
                    location = "Online"
                    location_elem = card.find(class_='location')
                    if location_elem:
                        location = location_elem.text.strip()
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": title,
                            "description": description,
                            "url": event_url,
                            "location": location,
                            "remote": "online" in location.lower() or "virtual" in location.lower(),
                            "tags": ["event", "eventbrite"]
                        },
                        opportunity_type="event"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing event card: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from Eventbrite")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping Eventbrite: {e}")
            return []

