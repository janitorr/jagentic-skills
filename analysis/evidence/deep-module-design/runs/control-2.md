# Deepening `ReportStore`

**Diagnosis.** `ReportStore` is a pass-through: `FetchAll` takes arbitrary SQL (`ReportStore.cs:15-17`), `Execute` takes writes (`:42`), and `Columns`/`TableName` expose the schema (`:54-68`). All three callers re-encode schema and SQL (`ReportApi.cs:11-13`, `Summary.cs:12-16`, `Export.cs:9-11`), and the test asserts column names (`Program.cs:41-44`). The seam belongs at the Data assembly boundary, not at ADO.NET.

**Proposed interface** (new `src/ShallowReport.Data/IReportStore.cs`):

```csharp
public sealed record ReportRow(
    long Id, string Title, string Category, double Total, string CreatedAt);

public interface IReportStore : IDisposable
{
    IReadOnlyList<ReportRow> ReadPage(int page, int size);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    IEnumerable<ReportRow> StreamAll();
}
```

Construction stays provider-specific, the interface does not:

```csharp
public static IReportStore Open(string path) => new SqliteReportStore(path);
// current class becomes internal sealed SqliteReportStore : IReportStore
```

The planned Postgres replica (`README.md:28-29`) becomes a second implementation. `StreamAll` yields while the reader is open, so the large-table constraint (`README.md:26`) holds.

**Callers**
- `ReportApi.ListReports(IReportStore store, ...)` calls `ReadPage`; page/size-to-offset math moves inside. It still maps rows to the unchanged `ReportDto` (`ReportApi.cs:15-18`).
- `Summary.TotalsByCategory(IReportStore, ...)` returns the store's dictionary directly; its SQL (`Summary.cs:12-15`) moves into the adapter.
- `Export.ExportCsv(IReportStore, TextWriter)` writes the fixed header `id,title,category,total,created_at`, then streams `foreach (var row in store.StreamAll())`. The header is the output contract, not a schema query.

**Tests.** Arrange-only `Program.cs:9-17` seeding moves to a small `Microsoft.Data.Sqlite` helper inside the test project; no production caller sees SQL. Tests use `IReportStore store = ReportStore.Open(path)`. Delete the `"schema"` check (`Program.cs:40-44`): it asserts the leak, while the export-header check and row order already pin observable behavior. The API, summary, and export checks stay unchanged in intent.

**Migration, behavior-preserving**
1. Add `ReportRow`, `IReportStore`, and `Open`; move existing query text and parameter binding verbatim into `SqliteReportStore`.
2. Run `dotnet run --project tests/ShallowReport.Tests` and save the output/CSV as a baseline.
3. Repoint the three callers to `IReportStore`, keeping method signatures and output identical.
4. Make `FetchAll`, `Execute`, `Columns`, `TableName` private/removed; `TableName` (`ReportStore.cs:68`) has no callers today.
5. Re-run tests; CSV bytes, DTO values, dictionary contents, and ordering must match step 2.
