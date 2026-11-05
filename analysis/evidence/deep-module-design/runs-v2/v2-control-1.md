# Deep Reporting Store: Proposal

## Seam

All callers depend on one interface in `ShallowReport.Data`, expressed in domain records, never SQL or columns:

```csharp
public sealed record ReportRecord(long Id, string Title, string Category, double Total, string CreatedAt);
public sealed record NewReport(long Id, string Title, string Category, double Total, string CreatedAt);

public interface IReportStore
{
    IReadOnlyList<ReportRecord> List(int page, int size);      // ORDER BY id, LIMIT/OFFSET
    ReportRecord? Get(long id);
    IReadOnlyList<ReportRecord> Search(string fragment, double minTotal);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    void ExportCsv(TextWriter output);                         // streams, never buffered
    void Add(NewReport report);
    void Import(IEnumerable<NewReport> reports);                // all-or-nothing
}

public sealed class DuplicateReportException : Exception { }
```

`ReportRecord` also carries `ToDelimitedRow()`, so `DebugRow`'s `id,title,category,total,created_at` order (ReportApi.cs:34-39, Export.cs:7-8) stays identical without callers naming columns.

## Adapters

- `SqliteReportStore : IReportStore` — sole SQL owner. Parameterized commands replace interpolation (Ingest.cs:17-20, ReportCatalog.cs:21-23); `List` keeps `ORDER BY id LIMIT @size OFFSET @offset` (ReportApi.cs:20-22). `Search` keeps `LIKE '%'||@fragment||'%'` and `total >= @min` (ReportCatalog.cs:21-23). `ExportCsv` reads columns from `PRAGMA table_info` and streams reader rows to the writer, replacing the cached `FetchAll` (Export.cs:12-20) while preserving header, order, and `ToString()` formatting. `Add` inserts one row; `Import` runs one `BEGIN`/`COMMIT` and rolls back fully on error (Ingest.cs:26-49). A constraint violation becomes `DuplicateReportException` wrapping the original.
- `CachingReportStore : IReportStore` — decorator. Caches `List`, `Get`, and `TotalsByCategory` by operation plus arguments, replacing the SQL-keyed cache (CachedReportStore.cs:16-27) and `ReportApi.PageCache` (ReportApi.cs:9-18). `Search` and `ExportCsv` bypass. `Add` clears after success; `Import` clears in `finally` (Ingest.cs:22-23, 46-47), so writes never leave stale data.
- `ReportStores.Open(cs)` — composition root returning `Caching(new Sqlite(cs))`; replaces static `ConnectionString` (ReportStore.cs:7). A `FakeReportStore` test adapter slots in at the same seam.

`TotalsByCategory` keeps the ordinal `start <= created_at < end` filter and category-ordered sums inside the adapter (Summary.cs:9-18), preserving exact output.

## Callers after

- `ReportApi.ListReports`: one `_store.List(page, size)` call, map to `ReportDto`; `DebugRow` uses `Get(id)` and `ToDelimitedRow()`; `PageCache` and `ClearCache` are deleted.
- `ReportCatalog`: `Get` and `Search` only.
- `Summary`: `TotalsByCategory(start, end)` only.
- `Export`: `store.ExportCsv(output)`; `FormatRow` moves into Data.
- `Ingest`: `store.Add(new NewReport(...))` and `store.Import(...)`; no cache calls.

Public signatures, ordering, pagination, CSV bytes, and duplicate/rollback behavior are unchanged.

## Tests after

- Bootstrap DDL stays in one test helper; seeds go through `Import`, not raw `INSERT` (Program.cs:9-13, 125-128).
- The `schema` test (Program.cs:100-107) asserts the CSV header line instead of `Columns("reports")`.
- Duplicate and import tests catch `DuplicateReportException` (Program.cs:61, 81); the rollback check (Program.cs:87) stays.
- New adapter test: streaming export yields rows without materializing, and list/totals reflect a write immediately.

## Reversible migration

1. Add the interface, records, and both adapters alongside existing code; tests green.
2. Move callers one commit each (Catalog, Api, Summary, Export, Ingest); both APIs coexist.
3. Move tests off raw SQL.
4. Delete `ReportStore`, `CachedReportStore`, `ReportApi.PageCache`, and `Ingest.Escape`.

Rollback is `git revert` of any single caller commit; legacy classes remain until step 4. No schema or data migration.
