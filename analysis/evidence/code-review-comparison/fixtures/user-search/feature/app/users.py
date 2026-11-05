from .auth import require_auth
from .audit import audit_log


@require_auth
def get_user(request, db):
    user = db.find_user(request.user.tenant_id, request.args["id"])
    if user is None:
        return {"error": "not found"}, 404
    return {"id": user["id"], "display_name": user["display_name"]}


def search_users(request, db):
    q = request.args.get("q", "")
    rows = db.query(
        f"SELECT id, email, display_name FROM users WHERE email LIKE '%{q}%'"
    )
    audit_log.info(f"search by {request.user.email}: {q}")
    return {"users": rows}
