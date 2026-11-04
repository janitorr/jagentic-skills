import test from "node:test";
import assert from "node:assert/strict";

import { searchTasks } from "../src/search.js";

function fakeDb(rows) {
  return {
    tasks: {
      findMany: async ({ where }) =>
        rows.filter(
          (row) =>
            row.userId === where.userId &&
            row.title.includes(where.title.contains),
        ),
    },
  };
}

test("returns only the authenticated user's matching tasks", async () => {
  const db = fakeDb([
    { id: "t1", userId: "u1", title: "Write report" },
    { id: "t2", userId: "u2", title: "Write report" },
    { id: "t3", userId: "u1", title: "Buy milk" },
  ]);

  const rows = await searchTasks(db, "u1", "report");

  assert.deepEqual(
    rows.map((row) => row.id),
    ["t1"],
  );
});
