# votes.py
from fastapi import APIRouter, HTTPException
from app.services.community_service import CommunityService
import logging

router = APIRouter(prefix="/votes", tags=["votes"])
service = CommunityService()

@router.post("/{report_id}")
def vote(report_id: str, voter_id: str, vote: int):
    logging.info(f"Received vote: report={report_id}, voter={voter_id}, vote={vote}")

    if vote not in [1, -1]:
        raise HTTPException(status_code=400, detail="Vote must be 1 or -1")

    try:
        result = service.vote_report(report_id, voter_id, vote)
        logging.info(f"Vote applied successfully: {result}")
        return result
    except Exception as e:
        logging.error(f"Vote failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
