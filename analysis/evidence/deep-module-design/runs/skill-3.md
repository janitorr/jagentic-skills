# Deepening ShallowReport.Data

**Module.** One responsibility: turn the reporting database into domain values. Callers are `ReportApi` (ReportApi.cs:9), `Summary` (Summary.cs:7), and `Export` (Export.cs:7); the test constructs the store at Program.cs:7. Today all three know the table name, column names, SQL, parameter syntax, and ADO types (ReportApi.cs:11-18, Summary.cs:12-19, Export.cs:9-17). The "module" only runs SQL.

**Interface.**

```csharp
public sealed record Report(long Id, string Title, string Category, double Total, string CreatedAt);
public sealed record ReportTable(
    IReadOnlyList<string> Columns,
    IEnumerable<IReadOnlyList<string?>> Rows);

public interface IReportStore
{
    IReadOnlyList<Report> List(int page = 1, int size = 20); // by id; 1-based page
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    ReportTable ReadForExport(); // columns in table order
}
```

Invariants: read-only; empty results are empty collections, never null; `TotalsByCategory` is half-open `[start, end)` and key-ordered, matching Summary.cs:13-15; `ReadForExport` rows stream in table order and use `null` for SQL NULL; callers must enumerate before disposing the store (README:26). No SQL, schema names, `SqliteConnection`, or `DBNull` appear in the interface.

**Seam.** At the existing caller boundary: `IReportStore` plus adapter `SqliteReportStore(string path)` in ShallowReport.Data, owning the connection (ReportStore.cs:7-13). The seam is real: SQLite now, a Postgres replica next quarter (README:28-29), and tests get an in-memory fake. CSV formatting stays in `Export`; the module returns values, not text.

**Alternatives.** (1) Rename `FetchAll` to `Query(ReportQuery)` — still leaks SQL and casts. (2) Separate `Columns()`/`ReadAll()` — two calls that can disagree on schema order. Chosen: three intention methods plus one export snapshot, so the header cannot drift from the rows.

**Callers after.** `ReportApi`: `store.List(page, size).Select(...)` into `ReportDto`. `Summary`: return `store.TotalsByCategory(start, end)` directly. `Export`: `var table = store.ReadForExport();`, write `string.Join(",", table.Columns)`, then stringify rows exactly as Export.cs:12-17 does.

**Tests after.** Seed the temp database with raw Sqlite in setup (replacing Program.cs:9-17; fixture construction, not assertion). Every assertion crosses `IReportStore`; the leaky schema test (Program.cs:40-44) becomes a `ReadForExport().Columns` order check, which is the CSV header. A `FakeReportStore` second adapter lets ReportApi/Summary/Export formatting be tested without SQL.

**Migration.** Add records, interface, and adapter beside `ReportStore`; existing tests stay green. Add parity tests running old and new against one seeded file. Switch `Export`, then `Summary`, then `ReportApi` in three commits, constructing `SqliteReportStore` at Program.cs:7. Delete `ReportStore` (including unused `TableName`, ReportStore.cs:68); confirm zero consumers with `rg 'ReportStore|FetchAll|\.Columns\(' src tests`. No persisted data changes, so the down path is reverting one caller commit while the old class still exists; the export-header test proves parity at each step.
