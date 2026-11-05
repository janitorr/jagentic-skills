using ShallowReport.Data;

namespace ShallowReport.App;

public static class Export
{
    public static string FormatRow(IReadOnlyDictionary<string, object?> row)
        => string.Join(",", row.Values.Select(value => value?.ToString() ?? string.Empty));

    public static void ExportCsv(TextWriter output)
    {
        var columns = CachedReportStore.Instance.Columns("reports");
        var rows = CachedReportStore.Instance.FetchAll(
            $"SELECT {string.Join(", ", columns)} FROM reports ORDER BY id");
        output.WriteLine(string.Join(",", columns));
        foreach (var row in rows)
        {
            output.WriteLine(string.Join(
                ",",
                columns.Select(column => row[column]?.ToString() ?? string.Empty)));
        }
    }
}
