from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import asyncio
import logging

from app.scrapers import get_scrapers_for_goal_type
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
        
        scrapers = get_scrapers_for_goal_type(goal_type)
        
        logger.info(f"Executing search with {len(scrapers)} scrapers for goal type: {goal_type}")
        
        # Prepare filters for scrapers
        filters = {
            "keywords": keywords,
            "location": location,
            "remote": remote,
            **goal_data.get("additional_filters", {})
        }
        
        # Remove keywords from filters to avoid duplicate argument
        scraper_filters = {k: v for k, v in filters.items() if k != 'keywords'}

        # Limit to 3 concurrent scrapers to prevent OOM
        semaphore = asyncio.Semaphore(3)

        async def scrape_with_limit(scraper):
            async with semaphore:
                return await self._scrape_with_logging(db, scraper, keywords, scraper_filters)

        tasks = [
            scrape_with_limit(scraper)
            for scraper in scrapers
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Commit scrape logs after all scrapers complete
        try:
            await db.commit()
        except Exception as e:
            logger.error(f"Error committing scrape logs: {e}")
            await db.rollback()
        
        all_opportunities = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Scraper failed: {result}")
                continue
            if result:
                all_opportunities.extend(result)
        
        logger.info(f"Found {len(all_opportunities)} total opportunities")
        
        stored_opportunities = await self._store_opportunities(db, all_opportunities, goal_data)
        
        return stored_opportunities
    
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
                    select(Opportunity).where(Opportunity.source_url == opp_data.get("url", ""))
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
                    source_url=opp_data.get("url", ""),
                    source_name=opp_data["source"],
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

