# Deepen `ReportStore`: reporting questions, not SQL

## Responsibility and callers

One sentence: answer the three reporting questions — paginated list, totals by category and date range, full export — without exposing SQL or schema. Callers are `ReportApi.ListReports` (ReportApi.cs:9-19), `Summary.TotalsByCategory` (Summary.cs:7-20), `Export.ExportCsv` (Export.cs:7-19), and tests (Program.cs:19-44). Today each builds SQL and reads columns (ReportApi.cs:11-18, Summary.cs:12-19, Export.cs:9-17), while `Columns()`/`TableName()` expose the schema (ReportStore.cs:54-68).

## Interface

```csharp
namespace ShallowReport.Data;

public sealed record Report(
    long Id, string Title, string Category, double Total, string CreatedAt);

public interface IReportStore : IDisposable
{
    IReadOnlyList<Report> List(int page, int size); // 1-based; offset is internal
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    IEnumerable<Report> ReadAll(); // lazy; enumerate while store is open
}
```

Invariants: `start` inclusive, `end` exclusive, ISO-8601 text (as today); totals contain one entry per category present; `ReadAll` streams rows ordered by id in `id,title,category,total,created_at` order; `Report` is a snapshot. No SQL text, table/column name, `SqliteConnection`, or `Microsoft.Data.Sqlite` type crosses the seam (README.md:28-29). Storage errors propagate unchanged; no new exception contract. `page`/`size` pass through without new validation, preserving current behavior.

`SqliteReportStore(path)` implements it and owns all SQL, parameters, and column mapping, moved from `ReportStore` (ReportStore.cs:15-68).

## Seam

At the existing App→Data boundary: App already references Data (ShallowReport.App.csproj:8) and each caller already accepts a store. Put the interface and `Report` in Data; App depends only on `IReportStore`. The planned Postgres replica (README.md:28-29) is the second adapter that makes the seam real. Keeping the seam at the raw methods would leave schema knowledge in callers.

## Alternatives

- Generic repository (`Query(sql)`, `GetById`) — rejected: leaks SQL or makes callers compose predicates; shallow.
- A `ReportQuery` filter object — rejected: larger surface for only three fixed questions.
- Caller-shaped methods (chosen): smallest interface, one method per reporting question, tests cross the same methods as callers.

## Callers after

```csharp
// ReportApi.cs
return store.List(page, size)
    .Select(r => new ReportDto(r.Id, r.Title, r.Total)).ToList();

// Summary.cs
return store.TotalsByCategory(start, end);

// Export.cs
output.WriteLine("id,title,category,total,created_at");
foreach (var r in store.ReadAll())
    output.WriteLine($"{r.Id},{r.Title},{r.Category},{r.Total},{r.CreatedAt}");
```

DTOs and public output are unchanged; export now streams instead of buffering (README.md:26).

## Tests after

Seeding (Program.cs:9-17) moves to a test fixture that creates the SQLite file directly; that is arrange input, not an assertion. Delete the `Columns("reports")` check (Program.cs:40-44): line 38 already guards column order through output. Assert list pages 1-2, summary, and full CSV text through `IReportStore`. No test calls `FetchAll`, `Execute`, `Columns`, or `TableName`.

## Migration (expand, migrate, contract)

1. Add `Report` and `IReportStore`; make `ReportStore` implement it by delegating to existing methods. Existing tests stay green.
2. Move one caller per commit to its typed method; run tests each time.
3. Switch tests to fixture setup and the interface; remove the schema assertion.
4. Inline the SQL into the implementation, remove `FetchAll`/`Execute`/`Columns`/`TableName`, rename to `SqliteReportStore`.
5. Down path: steps 1-3 are additive and revertible; keep old methods until step 4. Check zero consumers with `rg '\b(FetchAll|Columns|TableName|Execute)\b' src tests` and `dotnet run --project tests/ShallowReport.Tests`.
