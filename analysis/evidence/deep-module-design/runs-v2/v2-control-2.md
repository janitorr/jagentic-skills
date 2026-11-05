# Deepen `ShallowReport.Data`: schema-free reporting access

Current layer is a passthrough: it exposes `SqliteConnection`, raw SQL, row
dictionaries, `Columns`, and `TableName` (`src/ShallowReport.Data/ReportStore.cs:17-66`);
callers therefore own query text, ordering, schema, and escaping. Two caches
exist (`CachedReportStore.cs:5-25`, `ReportApi.cs:9-31`) and writes must clear
both manually (`Ingest.cs:22-23,46-47`).

## Interface

```csharp
public sealed record Report(long Id, string Title, string Category,
                            double Total, string CreatedAt);

public interface IReportReader {
    IReadOnlyList<Report> List(int page, int size);              // ORDER BY id
    Report? Find(long id);
    IReadOnlyList<Report> Search(string titleFragment, double minTotal);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    void ExportCsv(TextWriter output);                            // streams
}

public interface IReportWriter {
    void Add(Report report);                                      // duplicate throws
    void Import(IEnumerable<Report> reports);                     // one transaction
}

public interface IReportStore : IReportReader, IReportWriter { }
```

## Seam and adapters

The seam is `IReportStore`, wired once at a composition root
(`ReportAccess.Configure(IReportStore)` / `ResetForTests(...)`). Two adapters:

- **`SqliteReportStore`** — the only type knowing the schema. Parameterized
  statements, `PRAGMA table_info`, ordered reads, one `BEGIN/COMMIT/ROLLBACK`
  for `Import`, and a `SqliteDataReader` loop for `ExportCsv` so rows are never
  materialized (satisfies `README.md:29`). Totals stay in C# inside the adapter
  using `string.CompareOrdinal` and `OrderBy(key)` (`Summary.cs:11-17`) to keep
  ordinal date bounds and culture ordering exactly.
- **`CachingReportStore`** — a decorator: caches `List/Find/Search/Totals` by
  argument values rather than SQL text; `ExportCsv` bypasses the cache so it
  streams; `Add`/`Import` delegate, then clear once. This replaces both caches,
  making freshness unconditional (`README.md:34`). A Postgres adapter later
  plugs in without interface change (`README.md:31`).

Behavior kept: `List` computes `(page-1)*size`; `Search` keeps `LIKE '%…%'` so
ASCII case-insensitivity and `%`/`_` wildcards are unchanged; duplicate ids
still let the provider exception escape, matching the test's
`SqliteException` check (`tests/.../Program.cs:61`); no new validation or
features. `ExportCsv` keeps column order and `value?.ToString() ?? ""`
(`Export.cs:8,18-20`).

## Callers after the change

- `ReportApi.ListReports` calls `Store.List(page,size)` and maps to `ReportDto`;
  `PageCache` and `ClearCache` are deleted (`ReportApi.cs:9-31,41`).
- `ReportApi.DebugRow` uses `Find(id)` and joins the same five fields in the
  same order (`ReportApi.cs:34-38`).
- `ReportCatalog` calls `Find`/`Search` (`ReportCatalog.cs:9,21-26`).
- `Summary` calls `TotalsByCategory` (`Summary.cs:9-18`).
- `Export` calls `ExportCsv(output)` (`Export.cs:12-15`).
- `Ingest` maps `ReportInput`→`Report` and calls `Add`/`Import`; all manual
  cache clearing and the `Escape`/SQL builder disappear (`Ingest.cs:18-48`).

## Tests; reversible migration

Tests `api`, `get`, `search`, `export` keep their assertions. `cache` drops the
`ReportApi.ClearCache()` call (`Program.cs:122`) and proves invalidation through
the write itself. `duplicate`/`import` are unchanged, including the rollback
check (`Program.cs:54-88`). The schema test (`Program.cs:100-107`) moves into
the Data adapter's tests; it is not an app-facing concern, and column order is
already covered by the export header (`Program.cs:97`). A single fixture helper
keeps the DDL and seeds via `Import`.

Migration, one commit per caller, each independently revertible:

1. Add `Report`, the interfaces, both adapters, and a flag-selected composition
   root beside the old classes.
2. Port `Summary`, `Export`, `ReportCatalog`, `ReportApi`, `Ingest`; run tests
   after each.
3. Delete `ReportStore`/`CachedReportStore` and `PageCache` only after all
   callers pass.

Rollback is flipping the flag or reverting a caller commit; the old path stays
intact until step 3.
