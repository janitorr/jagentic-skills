import unittest

from app.users import get_user, search_users


class FakeRequest:
    def __init__(self, args, user):
        self.args = args
        self.user = user


class FakeUser:
    def __init__(self, tenant_id="tenant-a", email="agent@example.com"):
        self.tenant_id = tenant_id
        self.email = email


class FakeDB:
    def find_user(self, tenant_id, user_id):
        return {"id": user_id, "tenant_id": tenant_id, "display_name": "Alice"}

    def query(self, sql, params=()):
        return [{"id": "u1", "email": "alice@example.com", "display_name": "Alice"}]


class GetUserTest(unittest.TestCase):
    def test_returns_profile(self):
        result = get_user(FakeRequest({"id": "u1"}, FakeUser()), FakeDB())
        self.assertEqual(result, {"id": "u1", "display_name": "Alice"})


class SearchUsersTest(unittest.TestCase):
    def test_returns_matches(self):
        result = search_users(FakeRequest({"q": "alice"}, FakeUser()), FakeDB())
        self.assertEqual(
            result,
            {
                "users": [
                    {
                        "id": "u1",
                        "email": "alice@example.com",
                        "display_name": "Alice",
                    }
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
