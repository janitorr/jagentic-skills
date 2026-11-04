import test from "node:test";
import assert from "node:assert/strict";

import { createApp } from "../src/app.js";
import { registerRoutes } from "../src/api.js";

test("health route responds", async () => {
  const app = createApp();
  registerRoutes(app);

  const response = await app.handle({ method: "GET", path: "/health" });

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { status: "ok" });
});

test("unknown route is 404", async () => {
  const app = createApp();

  const response = await app.handle({ method: "GET", path: "/missing" });

  assert.equal(response.status, 404);
});

test("parses the query string from the path", async () => {
  const app = createApp();
  app.get("/echo", (request) => ({ term: request.query.term }));

  const response = await app.handle({ method: "GET", path: "/echo?term=report" });

  assert.equal(response.status, 200);
  assert.deepEqual(response.body, { term: "report" });
});
