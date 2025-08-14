from typing import Sequence, Any

def paginate(query, page: int = 1, per_page: int = 20):
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "items": items}
