from typing import List, Dict, Any
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
import logging

logger = logging.getLogger(__name__)


class RemoteOKScraper(Crawl4AIBaseScraper):
    
    def __init__(self):
        super().__init__(
            source_name="remoteok",
            base_url="https://remoteok.com"
        )
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            url = f"{self.base_url}/api"
            
            data = await self._crawl_json(url)
            
            if not isinstance(data, list):
                return []
            
            opportunities = []
            
            for job in data[1:21]:
                try:
                    if not isinstance(job, dict):
                        continue
                    
                    title = job.get('position', 'Unknown Position')
                    company = job.get('company', 'Unknown Company')
                    description = job.get('description', '')
                    
                    job_url = job.get('url', '')
                    if not job_url.startswith('http'):
                        job_url = f"{self.base_url}{job_url}"
                    
                    tags = job.get('tags', [])
                    
                    salary_min = job.get('salary_min')
                    salary_max = job.get('salary_max')
                    compensation = {}
                    if salary_min or salary_max:
                        compensation = {
                            "min": salary_min,
                            "max": salary_max,
                            "currency": "USD"
                        }
                    
                    opportunity = self._normalize_opportunity(
                        {
                            "title": f"{title} at {company}",
                            "description": description,
                            "url": job_url,
                            "location": "Remote",
                            "tags": tags,
                            "compensation_info": f"${salary_min}-${salary_max}" if salary_min else None
                        },
                        opportunity_type="job"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    logger.warning(f"Error parsing job: {e}")
                    continue
            
            logger.info(f"Scraped {len(opportunities)} opportunities from RemoteOK")
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scraping RemoteOK: {e}")
            return []
