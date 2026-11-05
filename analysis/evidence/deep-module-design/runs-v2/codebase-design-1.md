# Deepening the reporting data access

**Diagnosis.** `ReportStore` is a pass-through to `SqliteConnection`: callers write SQL and read schema-shaped dictionaries (`ReportStore.cs:17-50`), while `Columns`/`TableName` expose the table (`:52-66`). Every caller rebuilds queries (`ReportApi.cs:20-23`, `ReportCatalog.cs:9-10,21-24`, `Summary.cs:9-18`, `Export.cs:12-14`, `Ingest.cs:18-20`). Caches are keyed by SQL strings plus a second page cache (`CachedReportStore.cs:5-25`, `ReportApi.cs:9-10`), so writes clear two caches (`Ingest.cs:21-23,44-48`). Delete the module and this SQL, mapping, and invalidation reappears in five callers.

**New interface** (Data project, no SQLite types):

```csharp
public sealed record ReportRecord(
    long Id, string Title, string Category, double Total, string CreatedAt);

public interface IReportStore
{
    IReadOnlyList<ReportRecord> List(int page, int size);
    ReportRecord? GetById(long id);
    IReadOnlyList<ReportRecord> Search(string titleFragment, double minTotal);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    IEnumerable<ReportRecord> StreamAll();
    void Add(ReportRecord report);
    void Import(IEnumerable<ReportRecord> reports);
}
```

Contract: `List` is 1-based, ordered by `Id`, offset `(page-1)*size` (today's formula, `ReportApi.cs:21-22`). `Search` is ordered by `Id` and keeps LIKE wildcard/case-insensitive semantics (`ReportCatalog.cs:22-23`). `Totals` covers `[start,end)`, ordinal keys. `StreamAll` is lazy, ordered by `Id`, never cached. `Add`/`Import` throw `DuplicateReportException`; `Import` is atomic; reads after a successful write are never stale. `ReportRecord` field order defines CSV columns (`Export.cs:15`). Single connection, single-threaded, as today.

**Seam and adapters.** The seam is `IReportStore` in `ShallowReport.Data`. `SqliteReportStore` holds parameterized SQL, mapping, transactions, duplicate translation, and `SequentialAccess` streaming; it can later route reads to the planned replica (`README.md:31`). `InMemoryReportStore` serves behaviour tests. A future `PostgresReportStore` is the second production adapter. `CachingReportStore` decorates either:

```csharp
public void Add(ReportRecord r)    { _inner.Add(r);    Invalidate(); }
public void Import(IEnumerable<ReportRecord> rs)
                                   { _inner.Import(rs); Invalidate(); }
```

It caches `List/Get/Search/Totals` by domain keys, not SQL, and invalidates only after a successful write. SQLite specifics—LIKE folding, `BINARY`/`"C"` date ordering, `SQLITE_CONSTRAINT_PRIMARYKEY`, `LIMIT/OFFSET`—stay inside the adapter.

**Callers.** `ReportApi.ListReports` maps `Store.List` to `ReportDto` and drops `PageCache`; `DebugRow` uses `GetById`. `ReportCatalog` maps `GetById`/`Search`. `Summary` returns `TotalsByCategory`. `Export` loops `StreamAll`, writes the same header. `Ingest.Add`/`Import` map `ReportInput` to `ReportRecord`. Public signatures and output are unchanged. `ReportData.Store` is the single composition root; the static App facade remains, tests replace the root.

**Tests.** Per `Run`, set `ReportData.Store = new CachingReportStore(new InMemoryReportStore(seed))`; delete DDL/seed SQL and temp DB handling (`Program.cs:4-13,120-127`). Assertions stay. `duplicate` catches `DuplicateReportException`; `import` still proves rollback; the `schema` test (`Program.cs:100-107`) is deleted because schema is implementation. A contract suite runs all seven operations against both adapters, covering ordering, paging, lazy streaming, duplicate failure, atomic import, and cache freshness.

**Reversible migration.** (1) Add the interface, records, adapters, and contract tests beside the old code; the old suite stays green. (2) Switch all five callers in one commit, since writes and both caches are one shared concern; remove `ClearCache`. (3) Delete `ReportStore`/`CachedReportStore` and the schema test. Revert (2) while the old classes remain, or (3) then (2). No data or schema migration.

**Why deeper.** One interface now carries SQL, mapping, paging, streaming, transactions, duplicate policy, and invalidation. Callers get leverage; maintainers get locality; tests cross the same seam.
