import unittest

from app.auth import AuthError
from app.users import get_user, search_users


class FakeRequest:
    def __init__(self, args, user, request_id="req-1"):
        self.args = args
        self.user = user
        self.request_id = request_id


class FakeUser:
    def __init__(self, tenant_id="tenant-a", email="agent@example.com"):
        self.tenant_id = tenant_id
        self.email = email


class FakeDB:
    def __init__(self):
        self.calls = []
        self.user_calls = []

    def find_user(self, tenant_id, user_id):
        self.user_calls.append((tenant_id, user_id))
        return {"id": user_id, "tenant_id": tenant_id, "display_name": "Alice"}

    def find_users(self, tenant_id, q, limit=20, cursor=None):
        self.calls.append((tenant_id, q, limit, cursor))
        return (
            [{"id": "u1", "display_name": "Alice", "email": "alice@example.com"}],
            "next-page",
        )


class GetUserTest(unittest.TestCase):
    def test_returns_profile(self):
        db = FakeDB()
        result = get_user(
            FakeRequest({"id": "u1"}, FakeUser(tenant_id="tenant-b")), db
        )
        self.assertEqual(result, {"id": "u1", "display_name": "Alice"})
        self.assertEqual(db.user_calls, [("tenant-b", "u1")])


class SearchUsersTest(unittest.TestCase):
    def test_scopes_tenant_and_paginates(self):
        db = FakeDB()
        result = search_users(
            FakeRequest(
                {"q": " ali ", "limit": "20", "cursor": "c1"},
                FakeUser(tenant_id="tenant-b"),
            ),
            db,
        )
        self.assertEqual(
            result,
            {
                "users": [{"id": "u1", "display_name": "Alice"}],
                "next_cursor": "next-page",
            },
        )
        self.assertEqual(db.calls, [("tenant-b", "ali", 20, "c1")])

    def test_default_limit_is_20(self):
        db = FakeDB()
        search_users(FakeRequest({"q": "ali"}, FakeUser()), db)
        self.assertEqual(db.calls, [("tenant-a", "ali", 20, None)])

    def test_limit_above_max_is_rejected(self):
        result = search_users(FakeRequest({"q": "ali", "limit": "51"}, FakeUser()), FakeDB())
        self.assertEqual(result, ({"error": "limit must be between 1 and 50"}, 422))

    def test_limit_bounds_are_accepted(self):
        for value in (1, 50):
            db = FakeDB()
            result = search_users(
                FakeRequest({"q": "ali", "limit": str(value)}, FakeUser()), db
            )
            self.assertNotIn("error", result)
            self.assertEqual(db.calls, [("tenant-a", "ali", value, None)])

    def test_limit_below_min_is_rejected(self):
        result = search_users(FakeRequest({"q": "ali", "limit": "0"}, FakeUser()), FakeDB())
        self.assertEqual(result, ({"error": "limit must be between 1 and 50"}, 422))

    def test_non_integer_limit_is_rejected(self):
        result = search_users(
            FakeRequest({"q": "ali", "limit": "abc"}, FakeUser()), FakeDB()
        )
        self.assertEqual(result, ({"error": "limit must be an integer"}, 422))

    def test_empty_query_is_rejected(self):
        result = search_users(FakeRequest({"q": "  "}, FakeUser()), FakeDB())
        self.assertEqual(result, ({"error": "q is required"}, 422))

    def test_missing_query_is_rejected(self):
        result = search_users(FakeRequest({}, FakeUser()), FakeDB())
        self.assertEqual(result, ({"error": "q is required"}, 422))

    def test_anonymous_is_rejected(self):
        db = FakeDB()
        with self.assertRaises(AuthError):
            search_users(FakeRequest({"q": "ali"}, None), db)
        self.assertEqual(db.calls, [])

    def test_logs_do_not_contain_pii(self):
        with self.assertLogs("audit", level="INFO") as captured:
            search_users(
                FakeRequest(
                    {"q": "ali"}, FakeUser()
                ),
                FakeDB(),
            )
        for record in captured.records:
            payload = dict(record.__dict__)
            self.assertEqual(payload.get("count"), 1)
            self.assertEqual(payload.get("request_id"), "req-1")
            for forbidden_key in ("q", "email", "names", "display_name", "query"):
                self.assertNotIn(forbidden_key, payload)
            for forbidden_value in (
                "alice@example.com",
                "agent@example.com",
                "ali",
                "Alice",
            ):
                self.assertNotIn(forbidden_value, str(payload))

    def test_request_id_is_sanitized(self):
        with self.assertLogs("audit", level="INFO") as captured:
            search_users(
                FakeRequest({"q": "ali"}, FakeUser(), request_id="x\r\nforged"),
                FakeDB(),
            )
        payload = dict(captured.records[0].__dict__)
        self.assertEqual(payload.get("request_id"), "xforged")
        self.assertNotIn("\n", payload.get("request_id"))
        self.assertNotIn("\r", payload.get("request_id"))


if __name__ == "__main__":
    unittest.main()
