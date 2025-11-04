from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from aiolimiter import AsyncLimiter
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field
from app.config import settings

try:
    from crawl4ai import AsyncWebCrawler
    from crawl4ai.extraction_strategy import LLMExtractionStrategy
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    AsyncWebCrawler = None
    LLMExtractionStrategy = None

logger = logging.getLogger(__name__)


class OpportunitySchema(BaseModel):
    """Schema for extracting opportunity data using LLM"""
    title: str = Field(description="Job title, event name, or opportunity title")
    company_or_organizer: Optional[str] = Field(description="Company name, event organizer, or host organization")
    description: Optional[str] = Field(description="Brief description or summary of the opportunity")
    location: Optional[str] = Field(description="Location (city, country, or 'Remote')")
    url: str = Field(description="Direct URL or link to the opportunity")
    tags: Optional[List[str]] = Field(description="Relevant tags, categories, or keywords")
    compensation_info: Optional[str] = Field(description="Salary range, payment info, or 'Paid/Unpaid'")


class Crawl4AIBaseScraper(ABC):
    
    def __init__(self, source_name: str, base_url: str, rate_limit: int = None):
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limit = rate_limit or settings.scraping_rate_limit
        self.limiter = AsyncLimiter(self.rate_limit, 1)
        self.user_agent = settings.scraping_user_agent
        self.robots_parser: Optional[RobotFileParser] = None
        
        if not CRAWL4AI_AVAILABLE:
            logger.warning("crawl4ai not available, falling back to basic scraping")
    
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
    async def _crawl_with_llm(
        self, 
        url: str,
        instruction: str = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl and extract structured data using LLM.
        More resilient to website structure changes.
        """
        if not await self._check_robots_txt(url):
            raise Exception(f"Blocked by robots.txt: {url}")
        
        async with self.limiter:
            if CRAWL4AI_AVAILABLE and LLMExtractionStrategy:
                default_instruction = f"""
                Extract all opportunities (jobs, speaking events, conferences, or listings) from this page.
                For each opportunity, extract:
                - Title/position name
                - Company/organizer name
                - Description (brief summary)
                - Location (or "Remote")
                - Direct URL/link
                - Any relevant tags or categories
                - Compensation information if available
                
                Only extract actual opportunities, ignore navigation, ads, or unrelated content.
                """
                
                extraction_strategy = LLMExtractionStrategy(
                    provider="openai/gpt-4o-mini",
                    api_token=settings.openai_api_key,
                    schema=OpportunitySchema.model_json_schema(),
                    extraction_type="schema",
                    instruction=instruction or default_instruction,
                    chunk_token_threshold=4000,
                    overlap_rate=0.1
                )
                
                async with AsyncWebCrawler(verbose=False) as crawler:
                    result = await crawler.arun(
                        url=url,
                        bypass_cache=True,
                        user_agent=self.user_agent,
                        extraction_strategy=extraction_strategy,
                        word_count_threshold=10
                    )
                    
                    if hasattr(result, 'extracted_content') and result.extracted_content:
                        import json
                        try:
                            extracted = json.loads(result.extracted_content)
                            if isinstance(extracted, list):
                                return extracted
                            elif isinstance(extracted, dict):
                                return [extracted]
                        except json.JSONDecodeError:
                            logger.error(f"Failed to parse LLM extraction: {result.extracted_content}")
                    
                    return []
            else:
                logger.warning(f"LLM extraction not available for {url}, returning empty list")
                return []
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def _crawl_json(self, url: str) -> Dict:
        """For API endpoints that return JSON directly"""
        if not await self._check_robots_txt(url):
            raise Exception(f"Blocked by robots.txt: {url}")
        
        async with self.limiter:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": self.user_agent,
                    "Accept": "application/json"
                }
                async with session.get(url, headers=headers, timeout=30) as response:
                    response.raise_for_status()
                    return await response.json()
    
    def _normalize_opportunity(
        self,
        raw_data: Dict[str, Any],
        opportunity_type: str
    ) -> Dict[str, Any]:
        """Normalize LLM-extracted data to our internal format"""
        return {
            "title": raw_data.get("title", ""),
            "description": raw_data.get("description", ""),
            "source_url": raw_data.get("url", ""),
            "source_name": self.source_name,
            "opportunity_type": opportunity_type,
            "location": raw_data.get("location"),
            "remote": "remote" in str(raw_data.get("location", "")).lower(),
            "compensation": self._parse_compensation(raw_data.get("compensation_info")),
            "tags": raw_data.get("tags", []),
        }
    
    def _parse_compensation(self, compensation_info: Optional[str]) -> Optional[Dict[str, Any]]:
        """Parse compensation string into structured format"""
        if not compensation_info:
            return None
        
        comp_lower = compensation_info.lower()
        if "paid" in comp_lower or "$" in compensation_info or "salary" in comp_lower:
            return {"type": "paid", "details": compensation_info}
        elif "unpaid" in comp_lower or "volunteer" in comp_lower:
            return {"type": "unpaid", "details": compensation_info}
        
        return {"type": "unknown", "details": compensation_info}
    
    @abstractmethod
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape opportunities from the source.
        Should call _crawl_with_llm() and normalize results.
        """
        pass
