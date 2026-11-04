import test from "node:test";
import assert from "node:assert/strict";

import { requireUser } from "../src/auth.js";

test("returns the session user id", () => {
  assert.equal(requireUser({ session: { userId: "u1" } }), "u1");
});

test("rejects a request without a session", () => {
  assert.throws(() => requireUser({}), { status: 401 });
});
