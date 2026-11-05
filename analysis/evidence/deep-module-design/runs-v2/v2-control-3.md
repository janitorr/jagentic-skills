# Deepen the reporting data-access module

## Problem

`ReportStore` exposes `Connection`, `FetchAll(sql)`, `Columns()`, and `TableName()` (`src/ShallowReport.Data/ReportStore.cs:17-66`). Every caller composes SQL and decodes schema dictionaries: `ReportApi.cs:20-28,36-37`, `ReportCatalog.cs:9-24`, `Summary.cs:9-18`, `Export.cs:12-21`, `Ingest.cs:18-21`. Cache keys are SQL/page strings (`CachedReportStore.cs:18-21`, `ReportApi.cs:9-30`), and export buffers the whole table (`Export.cs:13-21`) despite `README.md:29`.

## Interface

```csharp
public sealed record Report(long Id, string Title, string Category,
                            double Total, string CreatedAt);

public interface IReportStore
{
    IReadOnlyList<Report> ListPage(int page, int size);   // ORDER BY id
    Report? GetById(long id);
    IReadOnlyList<Report> Search(string titleFragment, double minTotal);
    IReadOnlyDictionary<string, double> TotalsByCategory(
        string startInclusive, string endExclusive);
    IEnumerable<Report> StreamAll();                      // lazy, ORDER BY id
    void Add(ReportInput report);
    void Import(IEnumerable<ReportInput> reports);
}
```

No SQLite type, SQL, dictionary, or column metadata crosses this seam. `Report` is the five fields in fixed order; App still maps to `ReportDto`. Search keeps `%fragment%` and `total >= min`. Totals keeps ordinal `start <= created_at < end`, group/order/sum (`Summary.cs:11-18`). Pagination keeps `LIMIT size OFFSET (page-1)*size` and id order. `StreamAll` bypasses caching and yields from an open reader, so export writes as it reads.

## Seam and adapters

- `SqliteReportStore : IReportStore` replaces `ReportStore`: owns `SqliteConnection`, uses parameterized commands (`@id`, `@take`, `@skip`, `@like`, `@start`), with `@like = "%" + fragment + "%"` to preserve wildcard behavior. `StreamAll` is an iterator over `using` command/reader. `Import` opens one transaction, inserts all, commits; any failure rolls back and rethrows (`Ingest.cs:29-48`). Unique-key violations become `DuplicateReportException` with the `SqliteException` as inner.
- `CachedReportStore : IReportStore` becomes a decorator over any store. It caches reads by method plus arguments, not SQL, and returns immutable lists. `Add`/`Import` delegate then clear all entries in `finally`; no write bypasses it. `StreamAll` delegates uncached. `ReportApi.PageCache` (`ReportApi.cs:9-30`) is deleted; the decorator is the sole cache.
- Composition root: `ReportData.Store`, defaulting to `new CachedReportStore(new SqliteReportStore(cs))`; `ReportData.Use(store)` is the test seam. A future `PostgresReportStore` plugs in without caller changes.

## Callers after

- `ReportApi`: `Store.ListPage(page, size)` then map to `ReportDto`; `DebugRow` calls `GetById` and `Export.FormatRow(Report)`.
- `ReportCatalog`: `GetById`/`Search`, then map to DTO.
- `Summary`: `TotalsByCategory(start, end)` directly.
- `Export`: write the fixed header `id,title,category,total,created_at`, then `foreach (var r in Store.StreamAll())` write `r` fields in order. Output is unchanged, including `1,Q1 revenue,finance,1200,2026-01-15`.
- `Ingest`: `Store.Add(report)` or `Store.Import(reports)`; no SQL or cache calls.

## Tests after

`Program.cs` injects an `InMemoryReportStore` seeded with `Report` values through `ReportData.Use`, dropping `Ddl`/`SeedData` and the schema-reaching test (`Program.cs:4-13,100-107`). Export still asserts the same header and four lines. New adapter tests seed via `SqliteReportStore` and assert duplicate rejection, import rollback (`id 4` absent), pagination/order, search, totals, and `StreamAll` field order. The cache test keeps its intent: add, then list sees four.

## Reversible migration

1. Add `Report`, `IReportStore`, and `InMemoryReportStore`; no caller moves.
2. Add `SqliteReportStore`; make old `ReportStore` and `CachedReportStore.Instance` delegate to it, keeping `FetchAll`/`Columns` working.
3. Move callers one at a time to `ReportData.Store`; the old façade keeps compiling.
4. Turn `CachedReportStore` into the decorator; delete `Connection`, `FetchAll`, `Columns`, and App caches.
5. Delete the façade and finish test cleanup.

Each step is independently revertible; step 2 lets old and new paths coexist. Run tests after every step and compare export lines and DTO values.
