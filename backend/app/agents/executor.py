from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import asyncio
import logging

from app.scrapers import get_scrapers_for_goal_type
from app.scrapers.crawl4ai_base import Crawl4AIBaseScraper
from app.services.tavily_client import get_tavily_service
from app.models.opportunity import Opportunity, OpportunityType
from app.models.scrape_log import ScrapeLog, ScrapeStatus
from app.services.embeddings import generate_embeddings_batch
from datetime import datetime

logger = logging.getLogger(__name__)


class ExecutorAgent:
    
    async def execute_search(
        self,
        db: AsyncSession,
        goal_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        goal_type = goal_data.get("goal_type", "job")
        keywords = goal_data.get("keywords", [])
        location = goal_data.get("location", "Remote")
        remote = goal_data.get("remote", False)
        goal_id = goal_data.get("goal_id", "unknown")
        
        all_opportunities = []
        
        # Step 1: Tavily web search for opportunity URLs
        tavily_service = get_tavily_service()
        tavily_results = await tavily_service.search_opportunities(goal_data)
        
        if tavily_results:
            logger.info(f"Tavily returned {len(tavily_results)} URLs for goal {goal_id}")
            
            # Step 2: Extract opportunities from Tavily URLs using generic Crawl4AI
            # Limit concurrent extractions to avoid overload
            semaphore = asyncio.Semaphore(3)
            
            async def extract_from_tavily_url(tavily_result):
                async with semaphore:
                    return await self._extract_from_url_with_crawl4ai(
                        db=db,
                        url=tavily_result.url,
                        goal_type=goal_type,
                        keywords=keywords,
                        source_name=f"tavily:{tavily_result.source}"
                    )
            
            # Cap Tavily extractions to a reasonable number (e.g., 10)
            max_tavily_urls = 10
            tavily_tasks = [
                extract_from_tavily_url(result)
                for result in tavily_results[:max_tavily_urls]
            ]
            
            tavily_extraction_results = await asyncio.gather(*tavily_tasks, return_exceptions=True)
            
            for result in tavily_extraction_results:
                if isinstance(result, Exception):
                    logger.error(f"Tavily URL extraction failed: {result}")
                    continue
                if result:
                    all_opportunities.extend(result)
            
            logger.info(f"Extracted {len(all_opportunities)} opportunities from Tavily URLs")
        else:
            logger.info(f"Tavily returned no results for goal {goal_id}")
        
        # Commit Tavily scrape logs
        try:
            await db.commit()
        except Exception as e:
            logger.error(f"Error committing Tavily scrape logs: {e}")
            await db.rollback()
        
        # Step 3: Deduplicate opportunities by URL
        all_opportunities = self._deduplicate_opportunities(all_opportunities)
        
        logger.info(f"Found {len(all_opportunities)} total unique opportunities for goal {goal_id}")
        
        # Step 4: Store opportunities in database with embeddings
        stored_opportunities = await self._store_opportunities(db, all_opportunities, goal_data)
        
        # Log final metrics summary
        self._log_search_metrics(
            goal_id=goal_id,
            goal_type=goal_type,
            tavily_urls_found=len(tavily_results),
            tavily_urls_extracted=min(len(tavily_results), 10),  # We cap at 10
            total_opportunities_found=len(all_opportunities),
            opportunities_stored=len(stored_opportunities)
        )
        
        return stored_opportunities
    
    def _log_search_metrics(
        self,
        goal_id: str,
        goal_type: str,
        tavily_urls_found: int,
        tavily_urls_extracted: int,
        total_opportunities_found: int,
        opportunities_stored: int
    ):
        """Log comprehensive search metrics for monitoring and debugging."""
        logger.info(
            f"Search metrics for goal {goal_id} ({goal_type}): "
            f"Tavily URLs found={tavily_urls_found}, "
            f"URLs extracted={tavily_urls_extracted}, "
            f"Opportunities found={total_opportunities_found}, "
            f"Opportunities stored={opportunities_stored}"
        )
    
    async def _extract_from_url_with_crawl4ai(
        self,
        db: AsyncSession,
        url: str,
        goal_type: str,
        keywords: List[str],
        source_name: str
    ) -> List[Dict[str, Any]]:
        """
        Extract opportunities from a single URL using generic Crawl4AI extraction.
        Logs the extraction attempt to ScrapeLog.
        """
        started_at = datetime.utcnow()
        
        log = ScrapeLog(
            source_name=source_name,
            status=ScrapeStatus.SUCCESS,
            started_at=started_at
        )
        
        try:
            # Use the generic extraction class method
            opportunities = await Crawl4AIBaseScraper.extract_from_url(
                url=url,
                goal_type=goal_type,
                keywords=keywords,
                source_name=source_name
            )
            
            log.opportunities_found = len(opportunities)
            log.completed_at = datetime.utcnow()
            log.status = ScrapeStatus.SUCCESS
            
            db.add(log)
            
            logger.debug(f"Extracted {len(opportunities)} opportunities from {url}")
            return opportunities
        
        except Exception as e:
            log.status = ScrapeStatus.FAILURE
            log.error_log = str(e)
            log.completed_at = datetime.utcnow()
            
            db.add(log)
            
            logger.error(f"Failed to extract from {url}: {e}")
            return []
    
    def _deduplicate_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Deduplicate opportunities by URL.
        Keeps the first occurrence of each unique URL.
        """
        seen_urls = set()
        deduped = []
        
        for opp in opportunities:
            url = opp.get("source_url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduped.append(opp)
        
        if len(opportunities) != len(deduped):
            logger.info(f"Deduplicated {len(opportunities)} → {len(deduped)} opportunities")
        
        return deduped
    
    async def _scrape_with_logging(
        self,
        db: AsyncSession,
        scraper,
        keywords: List[str],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        source_name = scraper.source_name
        started_at = datetime.utcnow()
        
        log = ScrapeLog(
            source_name=source_name,
            status=ScrapeStatus.SUCCESS,
            started_at=started_at
        )
        
        try:
            opportunities = await scraper.scrape(keywords=keywords, **filters)
            log.opportunities_found = len(opportunities)
            log.completed_at = datetime.utcnow()
            log.status = ScrapeStatus.SUCCESS
            
            # Note: Don't commit here - let parent transaction handle it
            db.add(log)
            
            return opportunities
            
        except Exception as e:
            log.status = ScrapeStatus.FAILURE
            log.error_log = str(e)
            log.completed_at = datetime.utcnow()
            
            # Note: Don't commit here - let parent transaction handle it
            db.add(log)
            
            logger.error(f"Scraper {source_name} failed: {e}")
            return []
    
    async def _store_opportunities(
        self,
        db: AsyncSession,
        opportunities: List[Dict[str, Any]],
        goal_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        if not opportunities:
            return []
        
        texts_for_embedding = [
            f"{opp['title']} {opp.get('description', '')[:500]}"
            for opp in opportunities
        ]
        
        try:
            embeddings = await generate_embeddings_batch(texts_for_embedding)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            embeddings = [None] * len(opportunities)
        
        stored = []
        for opp_data, embedding in zip(opportunities, embeddings):
            try:
                from sqlalchemy import select
                # Check if opportunity already exists by URL
                result = await db.execute(
                    select(Opportunity).where(Opportunity.source_url == opp_data.get("source_url", ""))
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    continue
                
                # Determine if remote based on location
                is_remote = (
                    opp_data.get("location", "").lower() in ["remote", "anywhere", "worldwide"] or
                    goal_data.get("remote", False)
                )
                
                opportunity = Opportunity(
                    title=opp_data["title"],
                    description=opp_data.get("description"),
                    source_url=opp_data.get("source_url", ""),
                    source_name=opp_data.get("source_name", "unknown"),
                    opportunity_type=OpportunityType(opp_data["opportunity_type"]),
                    location=opp_data.get("location"),
                    remote=is_remote,
                    compensation=opp_data.get("compensation"),
                    tags=opp_data.get("tags", []),
                    embedding=embedding,
                    raw_data=opp_data
                )
                
                db.add(opportunity)
                stored.append(opp_data)
                
            except Exception as e:
                logger.error(f"Error storing opportunity: {e}")
                continue
        
        await db.commit()
        logger.info(f"Stored {len(stored)} new opportunities")
        
        return stored

