from typing import List, Dict, Any, Optional
from aiolimiter import AsyncLimiter
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel, Field
from app.config import settings

try:
    from crawl4ai import AsyncWebCrawler, LLMConfig
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


class Crawl4AIBaseScraper:
    """
    Base scraper using Crawl4AI for LLM-powered extraction.
    Provides a generic extraction method for arbitrary URLs.
    No longer requires subclassing - use extract_from_url() class method directly.
    """
    
    def __init__(self, source_name: str = "Generic", base_url: str = "", rate_limit: int = None):
        self.source_name = source_name
        self.base_url = base_url
        self.rate_limit = rate_limit or settings.scraping_rate_limit
        self.limiter = AsyncLimiter(self.rate_limit, 1)
        self.user_agent = settings.scraping_user_agent
        self.robots_parser: Optional[RobotFileParser] = None
        
        if not CRAWL4AI_AVAILABLE:
            logger.warning("crawl4ai not available, falling back to basic scraping")
    
    async def _check_robots_txt(self, url: str) -> bool:
        # try:
        #     parsed = urlparse(url)
        #     robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
        #     if not self.robots_parser:
        #         self.robots_parser = RobotFileParser()
        #         self.robots_parser.set_url(robots_url)
        #         self.robots_parser.read()
            
        #     return self.robots_parser.can_fetch(self.user_agent, url)
        # except Exception as e:
        #     logger.warning(f"Error checking robots.txt for {url}: {e}")
        #     return True
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

                llm_config = LLMConfig(
                    provider="google/gemini-2.5-flash",
                    api_token=settings.google_api_key,
                )
                
                extraction_strategy = LLMExtractionStrategy(
                    llm_config=llm_config,
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

                    # Surface crawl-level failures (e.g., navigation timeouts)
                    if hasattr(result, "success") and not result.success:
                        err_msg = getattr(result, "error_message", "") or "Crawl failed"
                        logger.error("Crawl4AI run failed for %s: %s", url, err_msg)
                        raise RuntimeError(err_msg)
                    
                    if hasattr(result, 'extracted_content') and result.extracted_content:
                        import json
                        try:
                            extracted = json.loads(result.extracted_content)
                            logger.debug(
                                "Crawl4AI extraction for %s: count=%s, sample=%r",
                                url,
                                len(extracted) if isinstance(extracted, list) else 1,
                                extracted[:1] if isinstance(extracted, list) else [extracted]
                            )
                            if isinstance(extracted, list):
                                return extracted
                            elif isinstance(extracted, dict):
                                return [extracted]
                        except json.JSONDecodeError as e:
                            logger.error(
                                "Failed to parse LLM extraction for %s: %s (content: %s)",
                                url, e, result.extracted_content[:200]
                            )
                    
                    logger.debug("Crawl4AI extraction for %s returned empty", url)
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
    
    @staticmethod
    def build_instruction_for_goal_type(goal_type: str, keywords: List[str] = None) -> str:
        """
        Build a goal-type-specific extraction instruction for Crawl4AI.
        
        Args:
            goal_type: Type of opportunity (job, speaking, event, grant)
            keywords: Optional list of keywords to focus on
        
        Returns:
            Instruction string for LLM extraction
        """
        keywords_str = ", ".join(keywords[:3]) if keywords else "all relevant"
        
        if goal_type.lower() == "job":
            return f"""
            Extract job opportunities from this page.
            Focus on roles related to: {keywords_str}
            
            For each job listing, extract:
            - Job title and position
            - Company or employer name
            - Job description (brief summary)
            - Location (or "Remote" if applicable)
            - Direct URL to apply or view details
            - Required skills or tags
            - Salary, compensation, or equity information if shown
            
            Only extract actual job postings, not ads or company profiles.
            """
        elif goal_type.lower() == "speaking":
            return f"""
            Extract speaking opportunities (Call for Speakers, CFPs, speaker applications) from this page.
            Focus on events/topics related to: {keywords_str}
            
            For each opportunity, extract:
            - Event or conference name
            - Organizer or host organization
            - Description of the speaking opportunity
            - Event location (city/country or "Virtual/Online")
            - URL to apply or submit a proposal
            - Topic areas or tags
            - Speaker compensation (paid, travel covered, etc.) if mentioned
            - Deadline for applications if shown
            
            Only extract speaking opportunities, not attendee registrations.
            """
        elif goal_type.lower() == "event":
            return f"""
            Extract events, conferences, or meetups from this page.
            Focus on events related to: {keywords_str}
            
            For each event, extract:
            - Event name or title
            - Organizer or host
            - Event description
            - Location (venue, city, or "Virtual")
            - Registration or event details URL
            - Event categories or tags
            - Ticket price or registration fee if shown
            - Event date if visible
            
            Only extract actual events, not ads or general information.
            """
        elif goal_type.lower() == "grant":
            return f"""
            Extract grant or funding opportunities from this page.
            Focus on grants related to: {keywords_str}
            
            For each grant, extract:
            - Grant name or program title
            - Funding organization or foundation
            - Grant description and purpose
            - Eligibility or target recipients
            - Application URL or contact information
            - Focus areas or categories
            - Funding amount if mentioned
            - Application deadline if shown
            
            Only extract actual grant opportunities, not general information.
            """
        else:
            return f"""
            Extract opportunities (jobs, events, grants, or other listings) from this page.
            Focus on: {keywords_str}
            
            For each opportunity, extract:
            - Title or name
            - Organization or company
            - Description
            - Location (or "Remote")
            - Direct URL or link
            - Relevant tags or categories
            - Compensation or cost information if available
            
            Only extract actual opportunities, not ads or navigation.
            """
    
    @classmethod
    async def extract_from_url(
        cls,
        url: str,
        goal_type: str,
        keywords: List[str] = None,
        source_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Generic extraction method for arbitrary URLs.
        This is a class method that can be called without instantiation.
        
        Args:
            url: URL to extract from
            goal_type: Type of opportunity (job, speaking, event, grant)
            keywords: Optional list of keywords to focus extraction
            source_name: Optional source name (defaults to domain from URL)
        
        Returns:
            List of normalized opportunity dictionaries
        """
        # Determine source name from URL if not provided
        if not source_name:
            try:
                domain = urlparse(url).netloc
                source_name = f"tavily:{domain}"
            except Exception:
                source_name = "tavily:unknown"
        
        # Create a temporary instance for extraction
        instance = cls(source_name=source_name, base_url="", rate_limit=2)
        
        # Build instruction
        instruction = cls.build_instruction_for_goal_type(goal_type, keywords)
        
        try:
            # Extract raw opportunities
            raw_opportunities = await instance._crawl_with_llm(url, instruction)
            
            logger.debug(
                "Generic extraction from %s: raw count=%s, sample=%r",
                url,
                len(raw_opportunities),
                raw_opportunities[:1]
            )
            
            # Normalize opportunities
            normalized = []
            for raw_opp in raw_opportunities:
                if not isinstance(raw_opp, dict):
                    logger.warning(f"Skipping non-dict item from {url}: {type(raw_opp)}")
                    continue
                
                normalized_opp = instance._normalize_opportunity(raw_opp, goal_type)
                if normalized_opp.get("source_url"):
                    normalized.append(normalized_opp)
            
            if not normalized and raw_opportunities:
                logger.debug(
                    "Generic extraction from %s: normalization dropped all items, first raw=%r",
                    url,
                    raw_opportunities[0]
                )
            
            logger.info(f"Generic extraction from {url}: {len(normalized)} opportunities")
            return normalized
        
        except Exception as e:
            logger.error(f"Error in generic extraction from {url}: {e}", exc_info=True)
            raise
    
    async def scrape(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Legacy scrape method - now deprecated.
        Use extract_from_url class method instead for generic extraction.
        """
        logger.warning(
            f"scrape() called on {self.source_name} - this method is deprecated. "
            "Use Crawl4AIBaseScraper.extract_from_url() instead."
        )
        return []

