# Deep module: report data access

**Responsibility.** Report persistence and retrieval: query translation, row mapping, transactions, cache invalidation. Callers know intents, never SQL or schema.

**Callers.** `ReportApi.cs:12,34` (list, debug row), `ReportCatalog.cs:7,19`, `Summary.cs:7`, `Export.cs:10`, `Ingest.cs:15,26`; tests `Program.cs:17-107`.

## Interface

New seam at the existing `ShallowReport.Data` boundary: replace the pass-through surface of `ReportStore.cs:19-66` with intent methods over domain records.

```csharp
namespace ShallowReport.Data;
public sealed record Report(long Id, string Title, string Category, double Total, string CreatedAt);
public sealed record CategoryTotal(string Category, double Total);
public sealed class ReportConflictException(long id, Exception inner)
    : Exception($"report {id} already exists", inner);

public interface IReportStore : IDisposable
{
    IReadOnlyList<Report> List(int page, int size);        // 1-based page; ORDER BY id; OFFSET (page-1)*size
    Report? Get(long id);
    IReadOnlyList<Report> Search(string titleFragment, double minTotal); // contains; total >= min; ORDER BY id
    IReadOnlyList<CategoryTotal> Totals(string start, string end);       // start <= created_at < end; ORDER BY category
    IEnumerable<Report> StreamAll();                       // lazy, ORDER BY id, one live reader
    void Add(Report report);                               // duplicate id -> ReportConflictException
    void Import(IEnumerable<Report> reports);              // all-or-nothing; same conflict error
}
```

Invariants: ordering as commented; search is `LIKE` substring matching, so `%`/`_` stay wildcards; totals compare `created_at` as strings (start inclusive, end exclusive), grouped and ordered by category; `StreamAll` buffers nothing and must be fully enumerated or abandoned; `Add`/`Import` invalidate every cached read, including on rollback; no read is stale after a write. Parameters replace the interpolated SQL at `ReportCatalog.cs:9,23` and `Ingest.cs:18-20`.

## Seam and adapters

- `SqliteReportStore` (`IReportStore`): parameterized commands, `BEGIN`/`COMMIT`/`ROLLBACK`, cursor-yielding `StreamAll`, maps SQLite constraint errors to `ReportConflictException` with the original `SqliteException` inner.
- `CachingReportStore` decorator: per-instance cache keyed by method arguments for `List`/`Get`/`Search`/`Totals`; `StreamAll` passes through; `Add` and `Import` clear in `finally`. This replaces the SQL-keyed static cache at `CachedReportStore.cs:5-27`, whose keys leaked across connections.
- `InMemoryReportStore` in tests: second adapter, proving nothing SQLite-shaped crosses the seam.
- The app's page cache at `ReportApi.cs:9-31` and `ClearCache` calls at `Ingest.cs:22-23,46-47` disappear; one cache, one invalidation point.

Rejected: typed methods returning `Dictionary<string, object?>` (callers still name columns); a generic `Query<T>(sql)` (SQL stays in callers); per-operation handler classes (ceremony, no hidden behavior).

## After the change

```csharp
// ReportApi
public static IReadOnlyList<ReportDto> ListReports(IReportStore store, int page = 1, int size = 20)
    => store.List(page, size).Select(ToDto).ToList();
public static string DebugRow(IReportStore store, long id)
    => store.Get(id) is { } r ? Export.FormatRow(r) : string.Empty;

// Export: header id,title,category,total,created_at; then
foreach (var r in store.StreamAll())
    output.WriteLine($"{r.Id},{r.Title},{r.Category},{r.Total},{r.CreatedAt}");

// Ingest
store.Add(new Report(r.Id, r.Title, r.Category, r.Total, r.CreatedAt));
store.Import(inputs.Select(ToReport));
```

`FormatRow(Report)` joins Id, Title, Category, Total, CreatedAt, preserving the `"1,Q1 revenue,finance,1200,2026-01-15"` output at `Program.cs:27`. `Summary` returns `store.Totals(start, end)`; `ReportCatalog.Search` returns `store.Search(fragment, minTotal)`.

**Tests.** One contract suite runs against both adapters. Assertions in `Program.cs:17-98` stay unchanged. Duplicate/import catches change from `SqliteException` (`Program.cs:61,81`) to `ReportConflictException` — the one deliberate error-type change. The schema test (`Program.cs:100-107`) is deleted: it exists only to expose the leak. The harness constructs a fresh store per test, replacing `ResetForTests` (`Program.cs:121`); the SQLite fixture keeps the DDL (`Program.cs:4-7`) but seeds via `Import`.

## Reversible migration

1. Add interface, records, and three adapters beside the old classes; compile only.
2. Add `LegacyReportStoreAdapter` over `ReportStore`, copy the current SQL verbatim, and run the contract suite against it and the new adapter. Outputs must match.
3. Switch callers one at a time (list, get, search, totals, export, ingest), tests green after each. Ingest goes last, when both old cache-clear calls can go.
4. `rg "CachedReportStore|FetchAll|FetchOne|\.Columns\(|\.Connection"` must return nothing outside the legacy adapter; then delete `ReportStore.cs`, `CachedReportStore.cs`, and the adapter in a separate commit.

Down path: steps 1-3 are code-only; revert the caller commits, old classes still work. No schema or data change, so rollback needs no database action.
