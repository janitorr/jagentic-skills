# Deepen `ReportStore`: hide SQL and schema

## Seam

Place the seam at the public API of `src/ShallowReport.Data`, not at the callers. Callers depend on `IReportStore`; the only SQLite-aware code stays in `ReportStore` (`ReportStore.cs:15-68`). No `SqliteConnection`, SQL text, table/column names, or row dictionaries cross the boundary. This also satisfies `README.md:28-29` (Postgres replica): a future `PostgresReportStore` can implement the same contract.

## Interface

```csharp
public interface IReportStore : IDisposable
{
    IReadOnlyList<ReportListItem> List(int page, int size);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    void WriteCsv(TextWriter output);
}

public sealed record ReportListItem(long Id, string Title, double Total);
```

`ReportStore` implements this with the existing SQL copied verbatim from `ReportApi.cs:11-13`, `Summary.cs:12-16`, and `Export.cs:9-11`, so ordering, casts, and pagination do not change. `WriteCsv` writes the header `id,title,category,total,created_at` and streams rows from the open `SqliteDataReader` rather than materializing a list, satisfying `README.md:26`. Keeping CSV writing here is deliberate: if `Export` received typed rows it would still hardcode column names and order, which is the schema leak being removed. `Execute` becomes `internal` for test seeding; `FetchAll`, `Columns`, and `TableName` (`ReportStore.cs:15-68`) are deleted.

## Callers after change

- `ReportApi.ListReports(IReportStore store, ...)` calls `store.List(page, size)` and maps to the unchanged `ReportDto` (`ReportApi.cs:15-19`). SQL disappears.
- `Summary.TotalsByCategory(IReportStore store, ...)` calls `store.TotalsByCategory(...)`; its mapping is unchanged (`Summary.cs:17-19`). SQL disappears.
- `Export.ExportCsv(IReportStore store, TextWriter output)` becomes `store.WriteCsv(output)`; the signature and emitted CSV remain identical (`Export.cs:7-19`).

## Test after change

`tests/ShallowReport.Tests/Program.cs:7-45` still constructs `ReportStore` and seeds through the now-internal `Execute`, exposed with `InternalsVisibleTo("ShallowReport.Tests")`, since the read module has no write API. The three behavior checks at lines 19-38 are unchanged. Delete the schema assertion at lines 40-44: it duplicates the export-header check at lines 36-38, and the header is now the module's contract. If a schema check is still wanted, assert only the exported header.

## Migration

1. Add `IReportStore`, `ReportListItem`, and the three methods; leave the old methods temporarily. Run `dotnet run --project tests/ShallowReport.Tests`.
2. Switch `ReportApi`, then `Summary`, then `Export`; run tests after each. CSV output should be byte-identical for the fixture.
3. Update the test and remove its `Columns` usage.
4. Delete `FetchAll`, `Columns`, and `TableName`, make `Execute` internal, and run tests again.

This changes only the dependency direction: behavior, SQL semantics, and public output stay the same.
