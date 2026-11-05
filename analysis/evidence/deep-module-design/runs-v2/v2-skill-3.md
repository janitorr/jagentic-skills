# Reporting data access: one store seam

**Module.** `IReportStore` owns the reports store: five reads and two writes, without exposing provider or schema. Callers: `ReportApi`, `ReportCatalog`, `Summary`, `Export`, `Ingest` (README:9-13); tests cross the same seam (Program.cs).

**Today's leak.** `ReportStore` exposes `Connection`, `FetchAll(sql)`, `Execute(sql)`, `Columns`, `TableName` (ReportStore.cs:17-66); every caller builds SQL (ReportApi.cs:20-23, ReportCatalog.cs:9,21-26, Summary.cs:9, Export.cs:12-14, Ingest.cs:18-21); tests build DDL and assert on `Columns` (Program.cs:4-13,100-107). Two caches (CachedReportStore.cs:5-27, ReportApi.cs:9-10) need manual clearing (Ingest.cs:22-23,46-47).

**Interface.**

```csharp
public interface IReportStore
{
    IReadOnlyList<Report> List(int page, int size);   // 1-based page, id order
    Report? GetById(long id);
    IReadOnlyList<Report> Search(string titleFragment, double minTotal);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    void Add(ReportInput report);
    void Import(IEnumerable<ReportInput> reports);
    void WriteCsv(TextWriter output);                 // streams header then rows
}

public sealed record Report(long Id, string Title, string Category,
                            double Total, string CreatedAt);
```

`ReportInput` moves from App/Ingest.cs:6-11 into Data.

Invariants: `List` returns at most `size` rows in ascending id with the same `LIMIT/OFFSET` semantics as ReportApi.cs:21-22; `GetById` is null when absent; `Search` keeps `LIKE '%…%' AND total >= …` and id order (ReportCatalog.cs:21-23); totals use ordinal half-open `[start, end)` and ordinal-sorted keys (Summary.cs:11-18); `WriteCsv` yields the header and one row at a time in id order; `Add` throws `DuplicateReportException` for an existing id; `Import` is atomic and rethrows with nothing persisted; every read observes the latest completed write. No `Sqlite*` type appears in the interface.

**Seam and adapters.** The seam replaces `ReportStore`/`CachedReportStore` at the existing caller boundary. `SqliteReportStore` owns the connection, the DDL (`CREATE TABLE IF NOT EXISTS`), parameterized SQL, the import transaction, and translates primary-key violations to `DuplicateReportException`. `CachingReportStore` is a decorator: it caches `List`/`GetById`/`Search`/`TotalsByCategory` by arguments and invalidates on `Add`/`Import` in `finally`; `WriteCsv` passes through uncached. A future `PostgresReportStore` satisfies the same seam (README:31). `ReportStoreFactory.Open(connectionString)` composes the decorator over SQLite.

Parameterization removes the injection at ReportCatalog.cs:23; a `%` or `_` in the fragment still acts as a wildcard because the pattern is passed as `%{fragment}%`.

**Alternatives rejected.** A generic `Query<T>(spec)`/expression repository still makes callers describe query shape and gives opaque cache keys. Keeping the class and adding methods beside `FetchAll` leaves the seam non-substitutable and the cache entangled with persistence.

**Callers.** App classes become instance classes taking `IReportStore`:

```csharp
public sealed class ReportApi(IReportStore store)
{
    public IReadOnlyList<ReportDto> ListReports(int page = 1, int size = 20)
        => store.List(page, size).Select(ReportDto.From).ToList();
    public string DebugRow(long id)
        => store.GetById(id) is { } r ? Export.FormatRow(r) : string.Empty;
}
```

`ReportApi.PageCache` and `ClearCache` disappear. `Ingest.Add`/`Import`, `Summary.TotalsByCategory`, and `ReportCatalog` delegate; `Export.ExportCsv` calls `WriteCsv`; `FormatRow(Report)` keeps today's `value?.ToString()` output (Export.cs:7-8). `ReportDto`, JSON shape, and CSV bytes are unchanged.

**Tests.** `Run` calls `ReportStoreFactory.Open(path)` and seeds with `store.Import([...])` instead of DDL/`Execute` (Program.cs:120-127); `ResetForTests` goes away because the cache is per instance. Existing assertions stay. Duplicate and import tests catch `DuplicateReportException`; rollback still asserts `GetById(4) is null`. The schema test (Program.cs:100-107) is deleted, its intent covered by list-order and CSV-header checks. Add one streaming check: header reaches a counting `TextWriter` before the final row is read.

**Migration (reversible).**

1. Add `IReportStore`, `Report`, `ReportInput`, `SqliteReportStore`, `CachingReportStore`, and `ReportStoreFactory` beside the old types; prove them with parallel tests.
2. Switch callers one at a time to constructor injection through the factory; old classes remain.
3. Check zero consumers via `rg "CachedReportStore|FetchAll|FetchOne|\.Execute\(|\.Columns\(" src tests`; then delete the old classes separately.

Down path: steps 1-2 leave the old path intact, so reverting caller commits and redeploying the previous build restores behavior. No schema or data migration. Keep one caution: `TotalsByCategory` must sum `double` in id order in the adapter, not via SQL `SUM`, to keep today's floating-point results (Summary.cs:10-18). The duplicate exception type is the only observable delta, covered by updated tests.
