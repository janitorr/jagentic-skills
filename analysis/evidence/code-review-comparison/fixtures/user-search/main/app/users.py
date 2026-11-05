from .auth import require_auth


@require_auth
def get_user(request, db):
    user = db.find_user(request.user.tenant_id, request.args["id"])
    if user is None:
        return {"error": "not found"}, 404
    return {"id": user["id"], "display_name": user["display_name"]}
