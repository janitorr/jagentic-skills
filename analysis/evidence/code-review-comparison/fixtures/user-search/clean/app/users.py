from .audit import audit_log
from .auth import require_auth


@require_auth
def get_user(request, db):
    user = db.find_user(request.user.tenant_id, request.args["id"])
    if user is None:
        return {"error": "not found"}, 404
    return {"id": user["id"], "display_name": user["display_name"]}


@require_auth
def search_users(request, db):
    q = (request.args.get("q") or "").strip()
    if not q:
        return {"error": "q is required"}, 422

    try:
        limit = int(request.args.get("limit", 20))
    except (TypeError, ValueError):
        return {"error": "limit must be an integer"}, 422
    if limit < 1 or limit > 50:
        return {"error": "limit must be between 1 and 50"}, 422

    cursor = request.args.get("cursor")
    rows, next_cursor = db.find_users(
        request.user.tenant_id, q, limit=limit, cursor=cursor
    )
    audit_log.info(
        "user_search",
        extra={"count": len(rows), "request_id": getattr(request, "request_id", "-")},
    )
    return {
        "users": [
            {"id": row["id"], "display_name": row["display_name"]} for row in rows
        ],
        "next_cursor": next_cursor,
    }
