from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_search_service
from app.schemas.search import SearchRequest, SearchResult
from app.services.search import HybridSearchService

router = APIRouter()


@router.post("", response_model=list[SearchResult])
def search(
    request: SearchRequest,
    service: HybridSearchService = Depends(get_search_service),
) -> list[SearchResult]:
    try:
        return service.search(request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
