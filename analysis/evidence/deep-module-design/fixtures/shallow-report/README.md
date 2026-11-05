# Shallow Report

Internal reporting service. .NET 10 / C#. The only data-access module is
`src/ShallowReport.Data/ReportStore.cs`, with caching in
`CachedReportStore.cs`.

Callers:

- `src/ShallowReport.App/ReportApi.cs` — paginated list for the HTTP API.
- `src/ShallowReport.App/ReportCatalog.cs` — get by id and search.
- `src/ShallowReport.App/Summary.cs` — totals by category for a date range.
- `src/ShallowReport.App/Export.cs` — CSV export of the full table.
- `src/ShallowReport.App/Ingest.cs` — add one report or import a batch.

SQLite schema:

```sql
CREATE TABLE reports (
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL,
  total REAL NOT NULL,
  created_at TEXT NOT NULL
);
```

Constraints:

- The export must stream; the table can be large.
- The API must paginate.
- A Postgres read replica is planned next quarter; do not assume SQLite in
  the interface.
- A duplicate id must fail, and a batch import must be all-or-nothing.
- The cache must not serve stale data after a write.
- Behavior and public output must not change.

Run the tests:

```bash
dotnet run --project tests/ShallowReport.Tests
```
