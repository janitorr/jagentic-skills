# Deepen the reporting data-access layer

**Module.** `IReportStore` has one responsibility: turn report queries and writes into persistence, including ordering, pagination, transactions, and cache freshness. Callers are ReportApi, ReportCatalog, Summary, Export, Ingest (README.md:7-13). Deletion test: remove it and SQL text, row-to-object mapping, offset arithmetic, transaction handling, and cache invalidation reappear in five callers (`ReportApi.cs:20-30`, `ReportCatalog.cs:9-36`, `Summary.cs:9-18`, `Export.cs:12-20`, `Ingest.cs:17-48`). It earns its keep.

**Interface.** Move `ReportInput` (`Ingest.cs:6-11`) into Data and add a `Report` domain record; no SQL type crosses the seam.

```csharp
public interface IReportStore
{
    IReadOnlyList<Report> List(int page, int size);          // 1-based; ORDER BY id
    Report? GetById(long id);                                 // null when absent
    IReadOnlyList<Report> Search(string titleFragment, double minTotal); // ORDER BY id
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    IEnumerable<Report> StreamAll();                          // lazy; ORDER BY id
    void Add(ReportInput report);                             // DuplicateReportException
    void Import(IReadOnlyCollection<ReportInput> reports);    // atomic
}
public sealed record Report(long Id, string Title, string Category,
                            double Total, string CreatedAt);
```

Invariants: page arithmetic stays `(page-1)*size` (`ReportApi.cs:22`); search is the same substring `LIKE '%fragment%'` plus `total >= min`, ordered by id; totals use `start <= created_at < end`, category ascending (`Summary.cs:11-18`); `StreamAll` yields id,title,category,total,created_at in that order and must not buffer. `Add` rejects a duplicate id. `Import` commits all or rolls back all. Any write attempt invalidates cache. Callers never see `SqliteConnection`, SQL, `Columns`, or cache state (`ReportStore.cs:17-66`).

**Seam and adapters.** The existing call boundary is `CachedReportStore.Instance` (AGENTS.md:6); replace it with `IReportStore` injection at the App boundary. Adapters:

- `SqliteReportStore`: parameterized SQL, mapping, pagination, and transactions; absorbs `ReportStore.cs:19-66` and `Ingest.cs:17-49`.
- `CachingReportStore` decorator: read-through cache keyed by page, id, or totals; clears on Add/Import after commit or rollback. It never caches `Search` or `StreamAll`, matching today's direct search (`ReportCatalog.cs:24-26`) and streaming constraint.
- `InMemoryReportStore`: caller-test adapter.
- A Postgres read-replica adapter can replace reads later (README.md:31-32) untouched by callers.

**Callers after the change.** Convert the static classes to instance classes taking `IReportStore`; signatures and output stay. `ReportApi.ListReports` → `List`, its `PageCache` deleted (`ReportApi.cs:9-31`); `DebugRow` → `GetById` + `FormatRow`. `ReportCatalog` → `GetById`/`Search`. `Summary` → `TotalsByCategory`. `Export` writes the fixed header `id,title,category,total,created_at`, then iterates `StreamAll()`; this removes today's full buffer in `FetchAll` (`ReportStore.cs:19-37`) while producing identical CSV. `Ingest` → `Add`/`Import`; `Escape`, BEGIN/COMMIT, and both `ClearCache` calls disappear (`Ingest.cs:17-48`).

**Tests after the change.** Replace raw DDL, seeding, and `ResetForTests` (`Program.cs:4-13,120-127`) with `InMemoryReportStore` seeded by `new Report(...)`; keep every output assertion (`Program.cs:17-98`). Delete the schema test (`Program.cs:100-107`), which reached through the seam; the export test already fixes column order. Adapter tests use a temp SQLite database for duplicate rejection, rollback, ordering, and lazy streaming. Duplicate assertions (`Program.cs:61,81`) expect `DuplicateReportException`; rejection and rollback behavior is unchanged.

**Alternatives compared.** (1) `Query(sql, params)`/`Execute(sql)`: still leaks SQL and schema; rejected. (2) Separate `IReportPager`/`IReportSearch` per caller: duplicates mapping and cache rules; rejected. The semantic single interface wins on depth and locality.

**Reversible migration.** *Expand:* add the interface, adapters, and `DuplicateReportException` beside the old types; no schema change. *Migrate:* port callers one at a time behind `ReportData.UseNewStore`, keeping the old path live, and compare old/new outputs over the same fixture. *Contract:* when `rg "CachedReportStore|ReportStore\.Instance"` finds no production references, delete the old types and flag in a separate commit. Down path: flip the flag; the old store and cache remain until contract.
