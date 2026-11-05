using System.Globalization;
using ShallowReport.Data;

namespace ShallowReport.App;

public sealed record ReportInput(
    long Id,
    string Title,
    string Category,
    double Total,
    string CreatedAt);

public static class Ingest
{
    public static void Add(ReportInput report)
    {
        var total = report.Total.ToString(CultureInfo.InvariantCulture);
        var sql =
            "INSERT INTO reports (id, title, category, total, created_at) VALUES " +
            $"({report.Id}, '{Escape(report.Title)}', '{Escape(report.Category)}', {total}, '{Escape(report.CreatedAt)}')";
        CachedReportStore.Instance.Execute(sql);
        CachedReportStore.ClearCache();
        ReportApi.ClearCache();
    }

    public static void Import(IEnumerable<ReportInput> reports)
    {
        var store = CachedReportStore.Instance;
        store.Execute("BEGIN");
        try
        {
            foreach (var report in reports)
            {
                Add(report);
            }

            store.Execute("COMMIT");
        }
        catch
        {
            store.Execute("ROLLBACK");
            throw;
        }
        finally
        {
            CachedReportStore.ClearCache();
            ReportApi.ClearCache();
        }
    }

    private static string Escape(string value) => value.Replace("'", "''");
}
