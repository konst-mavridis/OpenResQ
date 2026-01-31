from fastapi import APIRouter, HTTPException, Request, Query
from app.services.community_service import CommunityService
import logging

router = APIRouter(prefix="/votes", tags=["votes"])
service = CommunityService()

@router.post("/{report_id}")
def vote(
    request: Request,
    report_id: str,
    voter_id: str = Query(...),
    vote: int = Query(...),
    device_fp: str = Query(...),
    lat: float = Query(...),
    lng: float = Query(...),
):
    ip = request.client.host

    logging.info(
        f"Vote | report={report_id} voter={voter_id} vote={vote} "
        f"ip={ip} device={device_fp} lat={lat} lng={lng}"
    )

    if vote not in (1, -1):
        raise HTTPException(400, "Vote must be 1 or -1")

    try:
        return service.vote_report(
            report_id=report_id,
            voter_id=voter_id,
            vote=vote,
            ip_address=ip,
            device_fp=device_fp,
            lat=lat,
            lng=lng,
        )
    except Exception as e:
        logging.error(f"Vote failed: {e}")
        raise HTTPException(400, str(e))
