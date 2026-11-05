# Deepening ReportStore

**Module:** `ShallowReport.Data` answers report questions — paged list, category totals, full export stream — without exposing SQL, schema, or provider.

Current leaks: `ReportStore.cs:15-18` and `:42-43` accept SQL text; `:54-68` expose `PRAGMA table_info`, `"reports"`, and string-keyed rows. Each caller re-embeds schema: `ReportApi.cs:11-13`, `Summary.cs:12-16`, `Export.cs:9-11`. Tests seed and assert schema through SQL (`Program.cs:9-17,41-44`).

**Interface** (new `IReportStore` in Data):

```csharp
public sealed record ReportListItem(long Id, string Title, double Total);
public sealed record ReportRow(long Id, string Title, string Category,
                               double Total, string CreatedAt);

public interface IReportStore : IDisposable
{
    IReadOnlyList<ReportListItem> List(int page = 1, int size = 20);
    IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end);
    ReportExportSource Export();
    void Seed(IEnumerable<ReportRow> rows); // test setup; schema stays internal
}

public sealed record ReportExportSource(
    IReadOnlyList<string> Columns,
    IEnumerable<IReadOnlyList<object?>> Rows); // lazy
```

Invariants: ordering unchanged (id; category), `start` inclusive / `end` exclusive, same formatting, no new validation — `page 0` keeps today's negative-offset behavior. `Rows` stream: enumerate before disposal, one active reader. `Columns` comes from the adapter, so callers never name columns.

**Seam:** the existing `ShallowReport.App` → `ShallowReport.Data` assembly boundary. `SqliteReportStore` is the only production adapter; the planned Postgres replica adapter and a test fake make it real. App references only `IReportStore`.

**After change:**
- `ReportApi`: `store.List(page, size).Select(r => new ReportDto(r.Id, r.Title, r.Total))`; delete SQL.
- `Summary`: `return store.TotalsByCategory(start, end);`
- `Export`: header from `export.Columns`, then each row with the same `?.ToString() ?? ""` (`Export.cs:15-17`).
- Tests: seed via `store.Seed([...])`; keep API/summary/CSV assertions (`Program.cs:19-38`); replace the schema peek (`:41-44`) with the existing header assertion, which now proves column order through the interface.
- `SqliteReportStore` owns the SQL moved from callers and maps reader columns to records.

**Alternatives rejected:** (1) rename `FetchAll` to `Query` — still SQL, shallow; (2) put `ExportCsv` in Data — leaks presentation/culture into storage. Chosen design keeps formatting in App and schema in Data.

**Migration:**
1. Add records/interface and `SqliteReportStore` beside existing code; move caller SQL in. Verify: tests pass on old call paths.
2. Switch `ReportApi`, then `Summary`, then `Export`, one commit each. Verify: `dotnet run --project tests/ShallowReport.Tests` after each.
3. Move seeding to `Seed`; replace the schema test.
4. Mark old members `[Obsolete]`; remove when `grep -rn "FetchAll\|Columns(\|TableName\|Execute(" src/ShallowReport.App tests` is empty.

Down path: revert the App/test commit; no schema or data changes, so the old class still works. The Postgres adapter lands later behind the same interface.
