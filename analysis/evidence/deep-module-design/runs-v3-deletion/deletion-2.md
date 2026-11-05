# Redesign: report data access

**Module.** `IReportStore`: "report persistence, ordered and cached, with no schema
or SQL in callers." **Deletion test:** delete it and ordering, pagination,
filtering, streaming, transactionality, and cache invalidation reappear in five
callers (`ReportApi.cs:9-31`, `ReportCatalog.cs:9-24`, `Summary.cs:9-18`,
`Export.cs:12-14`, `Ingest.cs:17-47`). It earns its keep.

## Interface

```csharp
public interface IReportStore {
  IReadOnlyList<ReportDto> List(int page, int size);              // id asc, page >= 1
  ReportDto? GetById(long id);
  IReadOnlyList<ReportDto> Search(string titleFragment, double minTotal);
  IReadOnlyDictionary<string,double> TotalsByCategory(string start, string end);
  void ExportCsv(TextWriter output);                              // streams
  void Add(ReportInput report);
  void Import(IEnumerable<ReportInput> reports);                  // atomic
  string DebugLine(long id);                                      // existing ReportApi.DebugRow output
  void Invalidate();                                              // cache only
}
```

**Contract.** Ordering is `id` ascending everywhere; `List` is 1-based with the
same `OFFSET (page-1)*size` arithmetic (`ReportApi.cs:22`). `Search` keeps LIKE
"contains" semantics and `total >= minTotal` (`ReportCatalog.cs:23`). Totals cover
`start <= created_at < end` by ordinal comparison and accumulate in id order, so
the doubles match today's `Summary.cs:11-18`. `ExportCsv` writes
`id,title,category,total,created_at` then one line per row, nulls as empty, never
disposes or flushes, and never materialises rows — `Export.cs:13-14` buffers the
whole table despite README:29; this restores streaming without changing bytes.
Duplicate id throws `DuplicateReportException` (SQLite extended code 1555) from
`Add`, and mid-`Import`, which rolls back so nothing persists. `Add`/`Import`
invalidate once after commit, so no reader sees stale data.

## Seam and adapters

The seam is the interface in `ShallowReport.Data` (AGENTS.md:5 keeps the driver
there). `SqliteReportStore` is the only file holding `SqliteConnection`, PRAGMA,
and parameterized commands. `CachedReportStore` becomes a decorator over
`IReportStore`, keyed by method plus arguments instead of SQL text; export is not
cached. `ReportStoreFactory.Open(connectionString)` returns the cached adapter;
the static `Instance`/`ConnectionString`/`ResetForTests` (`CachedReportStore.cs:14-34`)
and `Connection`/`Columns`/`TableName` (`ReportStore.cs:17-66`) are removed.

Rejected: (a) keeping SQL strings with helper methods — callers still learn the
schema; (b) `IQueryable<Report>` — ordering, pagination, and streaming are not
expressible and the provider leaks; (c) separate `IReportQueries`/`IReportWriter` —
the planned replica argues for it, but writes must invalidate the read cache, so
splitting invites stale reads.

## Callers after

- `ReportApi.cs:12-32` → `_store.List(page, size)`; delete `PageCache` (`:9`).
  `DebugRow` (`:34-39`) → `_store.DebugLine(id)`; `ClearCache` → `Invalidate()`.
- `ReportCatalog.cs:7-17,19-37` → `_store.GetById(id)`, `_store.Search(fragment, min)`.
- `Summary.cs:7-19` → `_store.TotalsByCategory(start, end)`.
- `Export.cs:10-22` → `_store.ExportCsv(output)`; `FormatRow` is absorbed.
- `Ingest.cs:15-49` → `_store.Add(report)`, `_store.Import(reports)`; both cache
  clears and the manual BEGIN/COMMIT disappear.

## Tests after

Fixture owns the DDL and file setup; seeding goes through `Import` (`Program.cs:9-13`
SQL is deleted). `ResetForTests` calls (`Program.cs:121,136`) become a fresh
`Open(cs)` per test. Duplicate and import tests (`:61,81`) catch
`DuplicateReportException`. The schema test (`:100-107`) is deleted; the export
header assertion (`:97`) already checks column order through the seam. The cache
test (`:45-52`) is unchanged — it tests behavior, not internals.

## Reversible migration

1. Add the interface and both adapters; old `ReportStore`/`CachedReportStore` stay.
   Verify: existing suite still green.
2. Switch callers one file at a time through the single factory point; old `Ingest`
   keeps clearing both caches during the window so mixed callers stay fresh.
   Verify: full suite after each file.
3. **Down path:** `git revert` the caller switch; the old store is still present and
   tested. No schema or data migration, so rollback is code-only.
4. Contract: `git grep -n "FetchAll\|FetchOne\|CachedReportStore.Instance\|\.Columns(\|Export.FormatRow"`
   must return nothing; then delete the old files and `FormatRow` (public, one
   internal caller at `ReportApi.cs:38`, none external) and note it in the changelog.
