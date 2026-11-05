# Deepen the report data-access layer

**Module.** One responsibility: own every report read and write — ordering, paging, streaming, atomicity, cache coherence — behind one interface. *Deletion test:* remove it and five callers each regrow SQL, row mapping, paging math, transactions, and cache invalidation (ReportApi.cs:20-31, ReportCatalog.cs:9-24, Summary.cs:9-18, Export.cs:12-20, Ingest.cs:18-48); it earns its keep.

**Interface.**

```csharp
public interface IReportStore
{
    IReadOnlyList<ReportRecord> List(int page, int size);                 // ORDER BY id, 1-based
    ReportRecord? Get(long id);
    IReadOnlyList<ReportRecord> Search(string fragment, double minTotal); // ORDER BY id
    IReadOnlyList<CategoryTotal> TotalsByCategory(string start, string end);
    ReportTable ReadTable(long? id = null);      // columns + lazy rows, ORDER BY id
    void Add(ReportRecord report);               // duplicate -> DuplicateReportException
    void Import(IEnumerable<ReportRecord> reports); // all-or-nothing
}

public sealed record ReportRecord(long Id, string Title, string Category, double Total, string CreatedAt);
public sealed record CategoryTotal(string Category, double Total);
public sealed record ReportTable(IReadOnlyList<string> Columns, IEnumerable<IReadOnlyList<object?>> Rows);
```

Invariants: `List` keeps `LIMIT size OFFSET (page-1)*size`; `Search` keeps `%fragment%` and `total >= minTotal`; totals cover `[start,end)` by ordinal `created_at`, category ascending (Summary.cs:11-18); `Rows` streams in id order, columns in schema order, and can be enumerated alongside other calls; `Add`/`Import` throw `DuplicateReportException(id)` with no partial row; any write, successful or not, invalidates all cached reads. No new capabilities.

**Seam and adapters.** The seam is the existing App→Data boundary. `SqliteReportStore` is the only SQLite-aware type and translates constraint 1555. `CachingReportStore` decorates it and becomes the sole cache, invalidating in `Add`/`Import` (replacing Ingest.cs:22-23,46-47 and ReportApi.cs:9-18,30-31). `InMemoryReportStore` is the second adapter for tests; `PostgresReportStore` follows (README.md:31). The composition root passes one shared decorated instance to every caller.

**Callers.** Each static class receives `IReportStore` via constructor or one composition root; outputs stay identical. Api calls `List` and maps to `ReportDto`, `DebugRow` uses `ReadTable(id)`, page cache deleted. Catalog calls `Get`/`Search`. Summary maps totals to its existing dictionary. Export writes `Columns`, then streams `Rows` (today it buffers at Export.cs:13-14, violating README.md:29). Ingest maps `ReportInput`→`ReportRecord` and calls `Add`/`Import`; `BEGIN`/`COMMIT`/`ROLLBACK` and `Escape` go (Ingest.cs:29-51).

**Tests.** Each `Run` builds its own graph, disposes it, and seeds through `Import`, not raw DDL (Program.cs:126-127), so `ResetForTests` goes (CachedReportStore.cs:29-35). Read schema through `ReadTable().Columns`, not `Columns("reports")` (Program.cs:100-107); catch `DuplicateReportException` at Program.cs:61,81 — same failure, no provider leak; cache test loses only `ReportApi.ClearCache` (Program.cs:122). One contract suite runs against both adapters.

**Migration (reversible).** (1) Add the interface and Sqlite adapter beside the old types; tests stay green. (2) Move one caller per commit, keeping old invalidations until its page cache dies. (3) Insert `CachingReportStore`; delete `PageCache` after Api moves. (4) Translate duplicates last. (5) When `grep -rn "FetchAll\|FetchOne\|\.Connection\|Columns(" src tests` shows only legacy files, delete `ReportStore`/`CachedReportStore`. Each step reverts by reverting its commit; no schema change, and dropping the decorator restores direct reads. Rejected: a `Query(sql)` wrapper (still leaks SQL) and split read/write interfaces (splits cache invalidation and doubles the surface).
