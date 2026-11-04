export function registerRoutes(app) {
  app.get("/health", () => ({ status: "ok" }));
}
