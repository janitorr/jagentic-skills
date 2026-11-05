# Reporting data-access redesign

**Seam.** Place one external seam in `ShallowReport.Data`: `IReportStore`. It replaces `ReportStore`/`CachedReportStore` (`ReportStore.cs:5-69`, `CachedReportStore.cs:3-36`). Every caller currently embeds SQL or schema: `ReportApi.cs:20-29,36-38`, `ReportCatalog.cs:9-16,21-36`, `Summary.cs:9-19`, `Export.cs:12-21`, `Ingest.cs:17-23,28-51`. Deleting the module would remove that knowledge from five files, so it earns its keep.

```csharp
public sealed record Report(long Id, string Title, string Category,
                            double Total, string CreatedAt);

public interface IReportStore
{
    IReadOnlyList<Report> List(int page, int size);              // id order
    Report? Get(long id);
    IReadOnlyList<Report> Search(string titleFragment, double minTotal);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    void ExportCsv(TextWriter output);                           // streams
    void Add(ReportInput report);
    void Import(IEnumerable<ReportInput> reports);               // atomic
}
```

The interface carries the invariants: `List` is 1-based, ordered by id, empty past the end; `Search` is ordered by id and keeps SQLite `LIKE` fragment semantics; totals are ordinal-ordered by category; export writes the canonical header then id-ordered rows; `Add` throws `DuplicateReportIdException`; `Import` either commits every row or none; reads reflect completed writes immediately. Export owns its header so no caller sees column names.

**Adapters.** `SqliteReportStore` is the only SQL/`SqliteConnection` user. It parameterizes queries, maps rows to `Report`, streams export directly from the open reader (unlike the current materializing `FetchAll`, `ReportStore.cs:19-37`), runs `Import` in one transaction, and translates `SQLITE_CONSTRAINT` to `DuplicateReportIdException`. `InMemoryReportStore` (dictionary plus lock, copy-on-write import) is the second adapter for fast contract tests and makes the seam real; a Postgres adapter later fits without caller changes. `CachingReportStore` decorates either adapter: it caches `List`, `Get`, `TotalsByCategory` (not the streaming export) under semantic keys and clears them only after a successful write, replacing both caches now split across `CachedReportStore.cs:5-27` and `ReportApi.cs:9-10`.

**Callers.**

- `ReportApi.ListReports(IReportStore store, int page = 1, int size = 20)` maps `Report` to `ReportDto`; `PageCache` and `ClearCache` go. `DebugRow` becomes `store.Get(id) is { } r ? Export.FormatRow(r) : ""` (`ReportApi.cs:34-39`), with `FormatRow` taking a `Report`.
- `ReportCatalog.GetById`/`Search` delegate and project to `ReportDto`; SQL and the raw reader at `ReportCatalog.cs:24-34` go.
- `Summary.TotalsByCategory` delegates; the adapter keeps the `start`-inclusive, `end`-exclusive ordinal comparison (`Summary.cs:11-13`), and ordinal key order is preserved with `SortedDictionary(StringComparer.Ordinal)`.
- `Export.ExportCsv` is one delegation; `FormatRow` still produces the same comma-joined text.
- `Ingest.Add`/`Import` delegate and drop `Escape`, `BEGIN`/`COMMIT`/`ROLLBACK`, and both cache clears (`Ingest.cs:17-51`). No caller names SQL, tables, or columns.

**Tests.** Each test builds `new CachingReportStore(new SqliteReportStore(cs))`, seeds through `Import`, then keeps the existing assertions on DTOs, search results, totals, and CSV lines (`Program.cs:17-98`). Duplicate and import tests expect `DuplicateReportIdException` instead of `SqliteException` (`Program.cs:61,81`); rollback stays (`:87`). The schema test (`:100-107`) is deleted because the header assertion at `:97` covers the same fact through the interface. The suite also runs against `InMemoryReportStore`; `ResetForTests` and page-cache clearing disappear.

**Migration (reversible).** 1) Add the records, interface, and adapters, moving `ReportInput` into `ShallowReport.Data`; leave old code untouched. 2) Add contract tests and run both adapters. 3) Switch callers one at a time to take `IReportStore`, keeping old overloads as delegating shims. 4) Switch tests to the new composition. 5) Delete `ReportStore`, `CachedReportStore`, `PageCache`, and shims. Steps 1-4 are additive; each is an independent commit, so revert by restoring the prior step. No schema or public output changes; the duplicate error becomes provider-neutral.
