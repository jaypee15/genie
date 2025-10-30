from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.models.opportunity import Opportunity
from app.schemas.opportunity import OpportunityResponse, OpportunityFilters
from app.agents.coordinator import CoordinatorAgent

router = APIRouter()
coordinator = CoordinatorAgent()


@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    goal_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    if goal_id and user_id:
        result = await coordinator.get_ranked_opportunities(
            db=db,
            goal_id=goal_id,
            user_id=user_id,
            limit=limit
        )
        
        if result["success"]:
            opportunities = []
            for item in result["opportunities"]:
                opp = item["opportunity"]
                opp_dict = OpportunityResponse.from_orm(opp).dict()
                opp_dict["relevance_score"] = item["relevance_score"]
                opportunities.append(OpportunityResponse(**opp_dict))
            return opportunities
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
    
    query = select(Opportunity).limit(limit).offset(offset)
    result = await db.execute(query)
    opportunities = result.scalars().all()
    
    return opportunities


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opportunity = result.scalar_one_or_none()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return opportunity

