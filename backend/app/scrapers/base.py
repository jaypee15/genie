from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import aiohttp
from aiolimiter import AsyncLimiter
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    
    def __init__(self, source_name: str, base_url: str, rate_limit: int = None):
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limit = rate_limit or settings.scraping_rate_limit
        self.limiter = AsyncLimiter(self.rate_limit, 1)
        self.user_agent = settings.scraping_user_agent
        self.robots_parser: Optional[RobotFileParser] = None
    
    async def _check_robots_txt(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            if not self.robots_parser:
                self.robots_parser = RobotFileParser()
                self.robots_parser.set_url(robots_url)
                self.robots_parser.read()
            
            return self.robots_parser.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _fetch(self, url: str, headers: Optional[Dict] = None) -> str:
        if not await self._check_robots_txt(url):
            raise Exception(f"Blocked by robots.txt: {url}")
        
        async with self.limiter:
            default_headers = {
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            
            if headers:
                default_headers.update(headers)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=default_headers, timeout=30) as response:
                    response.raise_for_status()
                    return await response.text()
    
    async def _fetch_json(self, url: str, headers: Optional[Dict] = None) -> Dict:
        if not await self._check_robots_txt(url):
            raise Exception(f"Blocked by robots.txt: {url}")
        
        async with self.limiter:
            default_headers = {
                "User-Agent": self.user_agent,
                "Accept": "application/json",
            }
            
            if headers:
                default_headers.update(headers)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=default_headers, timeout=30) as response:
                    response.raise_for_status()
                    return await response.json()
    
    def _normalize_opportunity(
        self,
        raw_data: Dict[str, Any],
        opportunity_type: str
    ) -> Dict[str, Any]:
        return {
            "title": raw_data.get("title", ""),
            "description": raw_data.get("description", ""),
            "source_url": raw_data.get("url", ""),
            "source_name": self.source_name,
            "opportunity_type": opportunity_type,
            "location": raw_data.get("location"),
            "remote": raw_data.get("remote", False),
            "compensation": raw_data.get("compensation"),
            "tags": raw_data.get("tags", []),
        }
    
    @abstractmethod
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

