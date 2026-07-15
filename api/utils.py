from typing import Optional, Dict, Any
from fastapi import Query


def pagination_params(limit: int = Query(50, ge=1, le=1000), offset: int = Query(0, ge=0)) -> Dict[str, int]:
    return {"limit": limit, "offset": offset}


def filter_params(search: Optional[str] = Query(None), sort: Optional[str] = Query(None)) -> Dict[str, Any]:
    return {"search": search, "sort": sort}
