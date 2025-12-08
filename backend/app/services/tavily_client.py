"""
Tavily web search client wrapper for opportunity discovery.
"""
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from tavily import AsyncTavilyClient
    TAVILY_AVAILABLE = True
except ImportError:
    logger.warning("tavily-python not installed. Tavily search will be unavailable.")
    TAVILY_AVAILABLE = False
    AsyncTavilyClient = None


class TavilyResult:
    """Normalized result from Tavily search."""
    def __init__(self, title: str, url: str, snippet: str, score: float, source: str):
        self.title = title
        self.url = url
        self.snippet = snippet
        self.score = score
        self.source = source
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "score": self.score,
            "source": self.source
        }


class TavilySearchService:
    """Service for performing Tavily web searches for opportunities."""
    
    def __init__(self):
        if not TAVILY_AVAILABLE:
            logger.error("Tavily client not available")
            self.client = None
            return
        
        if not settings.tavily_api_key:
            logger.error("TAVILY_API_KEY not configured")
            self.client = None
            return
        
        self.client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        logger.info("Initialized Tavily search client")
    
    def _is_enabled_for_goal_type(self, goal_type: str) -> bool:
        """Check if Tavily is enabled for a given goal type."""
        goal_type_lower = goal_type.lower()
        if goal_type_lower == "job":
            return settings.enable_tavily_for_jobs
        elif goal_type_lower == "speaking":
            return settings.enable_tavily_for_speaking
        elif goal_type_lower == "event":
            return settings.enable_tavily_for_events
        elif goal_type_lower == "grant":
            return settings.enable_tavily_for_grants
        return False
    
    def _build_search_query(self, goal_data: Dict[str, Any]) -> str:
        """Build a Tavily search query from goal data."""
        goal_type = goal_data.get("goal_type", "")
        keywords = goal_data.get("keywords", [])
        location = goal_data.get("location", "")
        remote = goal_data.get("remote", False)
        
        # Start with goal type and keywords
        query_parts = []
        
        if goal_type.lower() == "job":
            query_parts.append("job opportunities")
        elif goal_type.lower() == "speaking":
            query_parts.append("speaking opportunities call for speakers CFP")
        elif goal_type.lower() == "event":
            query_parts.append("events conferences")
        elif goal_type.lower() == "grant":
            query_parts.append("grants funding opportunities")
        
        # Add keywords
        if keywords:
            query_parts.extend(keywords[:3])  # Limit to top 3 keywords
        
        # Add location context
        if remote:
            query_parts.append("remote")
        elif location:
            query_parts.append(location)
        
        query = " ".join(query_parts)
        logger.debug(f"Built Tavily search query: {query}")
        return query
    
    def _get_search_params(self, goal_type: str) -> Dict[str, Any]:
        """Get Tavily search parameters based on goal type."""
        params = {
            "search_depth": settings.tavily_search_depth,
            "max_results": settings.tavily_max_results,
            "include_raw_content": False,
            "include_images": False,
        }
        
        goal_type_lower = goal_type.lower()
        
        # Set topic based on goal type
        if goal_type_lower == "job":
            params["topic"] = "general"
            params["time_range"] = "month"  # Recent job postings
        elif goal_type_lower in ["speaking", "event"]:
            params["topic"] = "general"
            params["time_range"] = "month"  # Upcoming events
        elif goal_type_lower == "grant":
            params["topic"] = "general"
            params["time_range"] = "year"  # Grants have longer timelines
        else:
            params["topic"] = "general"
        
        return params
    
    async def search_opportunities(self, goal_data: Dict[str, Any]) -> List[TavilyResult]:
        """
        Search for opportunities using Tavily.
        
        Args:
            goal_data: Dictionary containing goal information:
                - goal_type: Type of opportunity (job, speaking, event, grant)
                - keywords: List of keywords
                - location: Target location (optional)
                - remote: Whether to focus on remote opportunities
                - goal_id: Goal ID for logging
        
        Returns:
            List of TavilyResult objects
        """
        if not self.client:
            logger.warning("Tavily client not available, skipping search")
            return []
        
        goal_type = goal_data.get("goal_type", "")
        goal_id = goal_data.get("goal_id", "unknown")
        
        # Check if Tavily is enabled for this goal type
        if not self._is_enabled_for_goal_type(goal_type):
            logger.info(f"Tavily search disabled for goal type: {goal_type}")
            return []
        
        try:
            # Build search query
            query = self._build_search_query(goal_data)
            
            # Get search parameters
            params = self._get_search_params(goal_type)
            
            logger.info(
                f"Tavily search for goal {goal_id}: query='{query}', "
                f"depth={params['search_depth']}, max_results={params['max_results']}"
            )
            
            # Perform search
            response = await self.client.search(query, **params)
            
            # Extract and normalize results
            results = []
            raw_results = response.get("results", [])
            
            logger.info(f"Tavily returned {len(raw_results)} results for goal {goal_id}")
            
            # Track domain distribution for logging
            domain_counts: Dict[str, int] = {}
            
            for item in raw_results:
                url = item.get("url", "")
                if not url:
                    continue
                
                # Extract domain for logging
                try:
                    domain = urlparse(url).netloc
                    domain_counts[domain] = domain_counts.get(domain, 0) + 1
                except Exception:
                    domain = "unknown"
                
                result = TavilyResult(
                    title=item.get("title", ""),
                    url=url,
                    snippet=item.get("content", ""),
                    score=item.get("score", 0.0),
                    source=domain
                )
                results.append(result)
            
            # Log domain distribution
            if domain_counts:
                top_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                logger.info(
                    f"Tavily search goal {goal_id} - top domains: "
                    f"{', '.join(f'{d}({c})' for d, c in top_domains)}"
                )
            
            # Log quality metrics
            avg_score = sum(r.score for r in results) / len(results) if results else 0
            logger.info(
                f"Tavily quality metrics for goal {goal_id}: "
                f"avg_score={avg_score:.2f}, "
                f"unique_domains={len(domain_counts)}"
            )
            
            return results
        
        except Exception as e:
            logger.error(
                f"Error performing Tavily search for goal {goal_id}: {e}",
                exc_info=True
            )
            return []


# Singleton instance
_tavily_service: Optional[TavilySearchService] = None


def get_tavily_service() -> TavilySearchService:
    """Get or create the Tavily service singleton."""
    global _tavily_service
    if _tavily_service is None:
        _tavily_service = TavilySearchService()
    return _tavily_service

