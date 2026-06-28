from fastapi import APIRouter, HTTPException
from app.models.schemas import FactCheckRequest, FactCheckResponse
from app.services.fact_checker import verify_fact_wikipedia

router = APIRouter(tags=["Fact Check"])

@router.post("/factcheck", response_model=FactCheckResponse)
@router.post("/fact-check", response_model=FactCheckResponse)
def do_factcheck(payload: FactCheckRequest):
    try:
        result = verify_fact_wikipedia(payload.query)
        summary = result["summary"]
        
        # Append source URL to summary so the client gets both in the single-field schema
        if result.get("verified") and "source_url" in result:
            summary += f"\n\nSource Reference: {result['source_url']}"
            
        return FactCheckResponse(summary=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fact check failed: {str(e)}")
