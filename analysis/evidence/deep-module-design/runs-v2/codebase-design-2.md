# Deepening the reporting data module

## Today

`ReportStore` is shallow: its interface is `FetchAll(sql)`, `FetchOne(sql)`, `Execute(sql)`, `Columns()`, and `Connection` (`src/ShallowReport.Data/ReportStore.cs:17-66`). Every caller supplies SQL and schema (`ReportApi.cs:20-23`, `ReportCatalog.cs:9,21-23`, `Summary.cs:9`, `Export.cs:12-14`, `Ingest.cs:18-20`). Cache invalidation is caller knowledge: `Ingest` clears `CachedReportStore` and `ReportApi.PageCache` (`Ingest.cs:22-23,46-47`; `ReportApi.cs:9-10,30,41`). Delete the module and every caller rebuilds SQL, mapping, caching, and transactions.

## Proposed interface (the seam)

```csharp
public sealed record Report(long Id, string Title, string Category, double Total, string CreatedAt);
public sealed class DuplicateReportException(long id, Exception inner)
    : Exception($"report {id} already exists", inner);

public interface IReportStore
{
    IReadOnlyList<Report> List(int page = 1, int size = 20);              // ORDER BY id
    Report? Get(long id);
    IReadOnlyList<Report> Search(string titleFragment, double minTotal);  // ORDER BY id
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    void ExportCsv(TextWriter output);                                    // streams, ORDER BY id
    void Add(Report report);                                              // duplicate throws
    void Import(IEnumerable<Report> reports);                             // all-or-nothing
}
```

The interface carries the invariants: offset remains `(page-1)*size`; totals keep `start` inclusive, `end` exclusive, ordinal date comparison, and key order (`Summary.cs:12-18`); `Search` keeps today's LIKE case/wildcard behaviour; `ExportCsv` writes the same header and row text (`Export.cs:15-21`); a duplicate id fails; an import commits every row or none. No SQL, `SqliteConnection`, or column names appear.

## Adapters

- **`SqliteReportStore`** — parameterized commands, schema-to-`Report` mapping, paging, a streaming `SqliteDataReader` for export (removes the current buffering at `Export.cs:13` without changing output), one transaction for `Import`, and translation of unique-constraint failures (extended code 2067) to `DuplicateReportException`.
- **`InMemoryReportStore`** — a second, real adapter implementing the same contract over a list; it makes the seam real and lets contract tests run without a database.
- **`CachedReportStore`** — a decorator over any adapter. Keys are argument tuples, not SQL. It clears after a successful `Add` and in `finally` after `Import`, matching `Ingest.cs:22-23,44-48`. No statics; `ExportCsv` passes through unbuffered.
- A future `PostgresReportStore` is a drop-in read adapter because no provider type crosses the seam.

## Callers and tests after the change

- `ReportApi.ListReports`: `store.List(page,size).Select(r => new ReportDto(r.Id,r.Title,r.Total))`; delete `PageCache`, `ClearCache`, and the SQL (`ReportApi.cs:9-31,41`). `DebugRow`: `store.Get(id)` formatted in field order (`ReportApi.cs:34-39`).
- `ReportCatalog`: `store.Get(id)` and `store.Search(fragment,minTotal)`; delete the SQL and direct reader (`ReportCatalog.cs:9,21-34`).
- `Summary`: `store.TotalsByCategory(start,end)`; delete `SELECT *` and in-memory grouping (`Summary.cs:9-19`).
- `Export`: `store.ExportCsv(output)`; delete `Columns`, `FetchAll`, and `FormatRow` (`Export.cs:7-21`).
- `Ingest`: map `ReportInput` to `Report`, then `store.Add(...)` or `store.Import(...)`; delete `Escape`, `BEGIN/COMMIT`, and cache calls (`Ingest.cs:17-48`).
- Tests: build a fresh store per test — `InMemoryReportStore` for behaviour, plus one SQLite file test — and seed via `Add`; drop `ResetForTests`/`ClearCache` (`tests/ShallowReport.Tests/Program.cs:121-122,136`); catch `DuplicateReportException` (`Program.cs:61,81`); replace the schema-reaching test (`Program.cs:100-107`) with the existing export-header assertion (`Program.cs:97`). Run the same behaviour suite against both adapters.

## Reversible migration

1. Add the types, interface, adapters, and decorator beside the old store; touch no caller and keep the old suite green.
2. Move one caller per commit, preserving public output; verify after each.
3. Switch tests to injected stores and add contract tests; old store still present.
4. Delete `ReportStore`'s SQL surface, `CachedReportStore`'s statics, and caller caches.

No schema or data migration is needed. Reverting steps 1–3 restores the old path per commit; step 4 is a pure deletion. The one intentional observable change is duplicate adds throwing `DuplicateReportException`; if strict exception parity is required, let the adapter rethrow `SqliteException`, accepting the provider leak. Otherwise callers gain leverage from seven intent methods, and maintainers gain locality for schema, caching, and transaction changes.
