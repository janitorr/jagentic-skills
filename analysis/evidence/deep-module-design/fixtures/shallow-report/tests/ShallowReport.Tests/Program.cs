using ShallowReport.App;
using ShallowReport.Data;

const string Ddl =
    "CREATE TABLE reports (" +
    "id INTEGER PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL, " +
    "total REAL NOT NULL, created_at TEXT NOT NULL)";

const string SeedData =
    "INSERT INTO reports (id, title, category, total, created_at) VALUES " +
    "(1, 'Q1 revenue', 'finance', 1200.0, '2026-01-15'), " +
    "(2, 'Q1 costs', 'finance', 800.0, '2026-02-01'), " +
    "(3, 'Launch', 'product', 400.0, '2026-02-10')";

var failures = new List<string>();

Run("api", () =>
{
    var rows = ReportApi.ListReports(page: 1, size: 2);
    Check(
        "api rows",
        rows.Count == 2
        && rows[0] == new ReportDto(1, "Q1 revenue", 1200.0)
        && rows[1] == new ReportDto(2, "Q1 costs", 800.0));
    Check(
        "debug row",
        ReportApi.DebugRow(1) == "1,Q1 revenue,finance,1200,2026-01-15");
});

Run("get", () =>
{
    Check("get by id", ReportCatalog.GetById(1) == new ReportDto(1, "Q1 revenue", 1200.0));
    Check("get missing", ReportCatalog.GetById(99) is null);
});

Run("search", () =>
{
    var expensive = ReportCatalog.Search("Q1", 1000.0);
    Check("search filter", expensive.Count == 1 && expensive[0].Id == 1);

    var all = ReportCatalog.Search("Q1", 0.0);
    Check("search all matches", all.Count == 2 && all[0].Id == 1 && all[1].Id == 2);
});

Run("cache", () =>
{
    Check("seed count", ReportApi.ListReports(1, 10).Count == 3);
    Ingest.Add(new ReportInput(4, "New", "product", 50.0, "2026-02-20"));
    Check("cache invalidated", ReportApi.ListReports(1, 10).Count == 4);
    var totals = Summary.TotalsByCategory("2026-01-01", "2026-03-01");
    Check("summary after write", totals["product"] == 450.0);
});

Run("duplicate", () =>
{
    var rejected = false;
    try
    {
        Ingest.Add(new ReportInput(1, "Duplicate", "finance", 10.0, "2026-03-01"));
    }
    catch (Exception ex) when (ex.GetType().Name == "SqliteException")
    {
        rejected = true;
    }

    Check("duplicate rejected", rejected);
});

Run("import", () =>
{
    var rejected = false;
    try
    {
        Ingest.Import(
            new[]
            {
                new ReportInput(4, "New", "product", 50.0, "2026-03-01"),
                new ReportInput(1, "Duplicate", "finance", 10.0, "2026-03-01"),
            });
    }
    catch (Exception ex) when (ex.GetType().Name == "SqliteException")
    {
        rejected = true;
    }

    Check("import rejected", rejected);
    Check("import rolled back", ReportCatalog.GetById(4) is null);
});

Run("export", () =>
{
    var output = new StringWriter();
    Export.ExportCsv(output);
    var lines = output.ToString().Split('\n', StringSplitOptions.RemoveEmptyEntries);
    Check(
        "export output",
        lines.Length == 4 && lines[0] == "id,title,category,total,created_at");
});

Run("schema", () =>
{
    // This test reaches past the module to the schema.
    Check(
        "schema",
        CachedReportStore.Instance.Columns("reports").SequenceEqual(
            new[] { "id", "title", "category", "total", "created_at" }));
});

if (failures.Count > 0)
{
    Console.Error.WriteLine($"failed: {string.Join(", ", failures)}");
    return 1;
}

Console.WriteLine("all tests passed");
return 0;

void Run(string test, Action body)
{
    var path = Path.Combine(Path.GetTempPath(), $"shallow-report-{Guid.NewGuid():N}.db");
    CachedReportStore.ResetForTests($"Data Source={path}");
    ReportApi.ClearCache();
    try
    {
        var store = CachedReportStore.Instance;
        store.Execute(Ddl);
        store.Execute(SeedData);
        body();
    }
    catch (Exception ex)
    {
        failures.Add($"{test}: {ex.GetType().Name}: {ex.Message}");
    }
    finally
    {
        CachedReportStore.ResetForTests("Data Source=:memory:");
        try
        {
            File.Delete(path);
        }
        catch
        {
            // Best-effort cleanup for the throwaway fixture database.
        }
    }
}

void Check(string name, bool ok)
{
    if (!ok)
    {
        failures.Add(name);
    }
}
