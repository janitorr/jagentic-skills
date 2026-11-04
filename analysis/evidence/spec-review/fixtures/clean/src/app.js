export function createApp({ db } = {}) {
  const routes = new Map();

  return {
    get(path, handler) {
      routes.set(`GET ${path}`, handler);
    },
    async handle(request) {
      const [path, search = ""] = request.path.split("?");
      const params = new URLSearchParams(search);
      const query = {};
      for (const key of new Set(params.keys())) {
        const values = params.getAll(key);
        query[key] = values.length > 1 ? values : values[0];
      }

      const route = routes.get(`${request.method} ${path}`);
      if (!route) {
        return { status: 404, body: { error: "not found" } };
      }
      try {
        return {
          status: 200,
          body: await route({ db, ...request, path, query }),
        };
      } catch (error) {
        return { status: error.status ?? 500, body: { error: error.message } };
      }
    },
  };
}
