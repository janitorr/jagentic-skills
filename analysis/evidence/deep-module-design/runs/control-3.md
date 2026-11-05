# Deepening the reporting data-access module

**Leak.** `ReportStore` is a SQL passthrough: `FetchAll(sql, params)` (ReportStore.cs:15-40), `Execute` (42-52), `Columns` (54-66), and `TableName` (68). Callers embed both SQL and schema: ReportApi.cs:11-18, Summary.cs:12-19, Export.cs:9-17. The test also asserts the `reports` columns (Program.cs:41-44).

**Seam.** Put the seam at the `ShallowReport.Data` assembly boundary. App code compiles against `IReportReader`; the SQLite adapter stays internal behind a factory.

```csharp
namespace ShallowReport.Data;

public sealed record ReportListItem(long Id, string Title, double Total);

public sealed class ReportExport
{
    public required IReadOnlyList<string> Columns { get; init; }
    public required IEnumerable<IReadOnlyList<object?>> Rows { get; init; }
}

public interface IReportReader : IDisposable
{
    IReadOnlyList<ReportListItem> List(int skip, int take);
    IReadOnlyDictionary<string, double> TotalsByCategory(string from, string toExclusive);
    ReportExport OpenExport();
}

public static class ReportStore
{
    public static IReportReader Open(string path) => new SqliteReportStore(path);
}
```

`SqliteReportStore` owns the connection, table name, column list, `PRAGMA`, and parameterized SQL. `List` applies `LIMIT/OFFSET` internally. Date bounds stay strings so the existing text comparisons are unchanged (Summary.cs:16). `OpenExport` returns column names plus a lazily enumerated row sequence, not a buffered list, honoring README.md:26 while keeping CSV content identical.

**Callers.**
- `ReportApi.ListReports` (ReportApi.cs:9-19) takes `IReportReader`, computes `(page - 1) * size`, calls `List`, and maps `ReportListItem` to the existing `ReportDto`. DTO and output are unchanged.
- `Summary.TotalsByCategory` (Summary.cs:7-20) takes `IReportReader` and returns `store.TotalsByCategory(start, end)`.
- `Export.ExportCsv` (Export.cs:7-19) takes `IReportReader`, writes `export.Columns`, then each row using the same `value?.ToString() ?? ""` cell conversion.

```csharp
public static IReadOnlyList<ReportDto> ListReports(IReportReader store, int page = 1, int size = 20)
    => store.List((page - 1) * size, size)
        .Select(r => new ReportDto(r.Id, r.Title, r.Total)).ToList();

var export = store.OpenExport();
output.WriteLine(string.Join(",", export.Columns));
foreach (var row in export.Rows)
    output.WriteLine(string.Join(",", row.Select(v => v?.ToString() ?? "")));
```

**Test.** Replace the DDL and inserts (Program.cs:9-17) with a typed, Data-owned fixture builder (`ReportStore.CreateFixture(path, rows)`, internal plus `InternalsVisibleTo`) so database setup remains inside Data. Delete the schema assertion (41-44); keep the `api rows`, `summary`, and `export header` checks (19-38) unchanged.

**Migration.**
1. Add the interface/types and adapter methods beside the old methods, moving each caller's SQL into Data.
2. Port ReportApi, Summary, and Export to `IReportReader`; run `dotnet run --project tests/ShallowReport.Tests` (AGENTS.md:6).
3. Switch the test to the fixture builder, remove the schema assertion, rerun, and diff the CSV byte-for-byte.
4. Delete `FetchAll`, `Execute`, `Columns`, and `TableName` (ReportStore.cs:15-68); remove imports my change orphaned.
5. For the planned Postgres replica, add `PostgresReportStore : IReportReader`; no caller changes.

Behavior is preserved: same rows, id ordering, pagination, totals, CSV header/content. No new operations.
