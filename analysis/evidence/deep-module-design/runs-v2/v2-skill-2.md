# Deep report store

**Responsibility.** One module owns the report read/write contract: SQL, schema
mapping, ordering, pagination, streaming, transactions, and cache freshness.
Deleting it would push all of that back into five callers.

**Interface** (`src/ShallowReport.Data`, models as records):

```csharp
public interface IReportStore
{
    IReadOnlyList<Report> List(int page, int size);
    Report? GetById(long id);
    IReadOnlyList<Report> Search(string titleFragment, double minTotal);
    IReadOnlyList<CategoryTotal> TotalsByCategory(string start, string end);
    void ExportCsv(TextWriter output);
    void Add(ReportDraft report);
    void Import(IEnumerable<ReportDraft> reports);
}
public sealed record Report(long Id, string Title, string Category, double Total, string CreatedAt);
public sealed record ReportDraft(long Id, string Title, string Category, double Total, string CreatedAt);
public sealed record CategoryTotal(string Category, double Total);
```

Contract:

- `List`: `ORDER BY id`, `LIMIT size OFFSET (page-1)*size`, page defaults live
  in callers (`ReportApi.cs:12,20-22`). `Search`: LIKE substring plus
  `total >= minTotal`, ordered by id (`ReportCatalog.cs:19-23`).
- `TotalsByCategory`: `start <= created_at < end` compared ordinally, grouped and
  ordered by category as today (`Summary.cs:11-18`).
- `ExportCsv`: header, then rows in id order, unquoted, `ToString()` values,
  written from a reader without buffering (`Export.cs:12-21`).
- `Add` fails when the id exists; `Import` is one transaction, all-or-nothing.
  Both invalidate every cached read in a `finally`, including on failure.
- `Add` still surfaces the driver's constraint exception unchanged (tests depend
  on `SqliteException`, `Program.cs:61,81`). Wrapping it in a domain error is a
  separate decision.
- No SQL, schema, connection, or cache method appears above.

**Seam and adapters.** The seam sits at the existing Data/App boundary.
`SqliteReportStore` owns commands, parameters, row mapping, and transactions.
`CachedReportStore` becomes a decorator caching List/GetById/Totals and clearing
on writes. A planned Postgres replica swaps only the inner adapter. Search and
export stay uncached, matching today (`ReportCatalog.cs:24` reads directly).
`ReportStores.Current` is the composition root, replacing
`CachedReportStore.Instance`.

**Callers after.**

- `ReportApi`: deletes `PageCache` and SQL (`ReportApi.cs:9-31`); `ListReports`
  projects `Current.List(page,size)`, `DebugRow` formats `Current.GetById(id)`,
  `ClearCache` goes away.
- `ReportCatalog`: `GetById`/`Search` delegate; no `Connection` (`:9-24`).
- `Summary`: returns `Current.TotalsByCategory(start,end)` as a dictionary; no
  row scan.
- `Export`: calls `Current.ExportCsv(output)`; `FormatRow` stays for `DebugRow`.
- `Ingest`: maps `ReportInput` to `ReportDraft`; no SQL, escaping, `BEGIN`, or
  cache clears (`Ingest.cs:15-51`).

**Tests after** (`Program.cs`). `Run` builds
`new CachedReportStore(new SqliteReportStore(path))`, assigns `ReportStores.Use`,
seeds through a test fixture helper, and keeps every assertion: duplicate and
rollback catch `SqliteException` (`:61,81`), cache invalidation checks List and
Summary after `Add` (`:47-51`). Delete the schema test's `Columns` call
(`:102-107`); the export header check (`:97`) already proves column names and
order. Add one contract test: every write invalidates List and Totals.

**Migration (reversible).**

1. Add records, interface, and both adapters; leave old classes untouched; run
   contract tests against the SQLite adapter.
2. Switch callers one commit at a time (Summary, Export, Catalog, Api, Ingest),
   keeping tests green. Old classes still serve any straggler.
3. Delete `ReportStore` and `CachedReportStore` only after
   `grep -R "FetchAll\|FetchOne\|Columns(\|ClearCache\|\.Connection" src` shows
   hits confined to `ShallowReport.Data`, plus one clean release.
4. Down path: revert the caller commit; old classes and the singleton still
   exist through step 2. The database is unchanged, so no data rollback.

**Alternatives rejected.** (a) Keep `Query(sql)` and let callers map rows: no
depth, schema still leaks. (b) Split read and write interfaces: every caller
needs two dependencies and cache invalidation straddles the seam. (c) Return
App DTOs from Data: reverses the dependency and still needs the write contract.
