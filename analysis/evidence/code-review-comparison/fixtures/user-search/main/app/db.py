class Database:
    def query(self, sql, params=()):
        raise NotImplementedError

    def find_user(self, tenant_id, user_id):
        raise NotImplementedError

    def find_users(self, tenant_id, q, limit=20, cursor=None):
        """Return tenant-scoped users matching q with a stable page order."""
        raise NotImplementedError
