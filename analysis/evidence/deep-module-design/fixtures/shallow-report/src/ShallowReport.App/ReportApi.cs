using ShallowReport.Data;

namespace ShallowReport.App;

public sealed record ReportDto(long Id, string Title, double Total);

public static class ReportApi
{
    private static readonly Dictionary<string, IReadOnlyList<ReportDto>> PageCache =
        new(StringComparer.Ordinal);

    public static IReadOnlyList<ReportDto> ListReports(int page = 1, int size = 20)
    {
        var cacheKey = $"{page}:{size}";
        if (PageCache.TryGetValue(cacheKey, out var cached))
        {
            return cached;
        }

        var sql =
            "SELECT id, title, total FROM reports ORDER BY id " +
            $"LIMIT {size} OFFSET {(page - 1) * size}";
        var rows = CachedReportStore.Instance.FetchAll(sql);
        var result = rows
            .Select(row => new ReportDto(
                (long)row["id"]!,
                (string)row["title"]!,
                (double)row["total"]!))
            .ToList();
        PageCache[cacheKey] = result;
        return result;
    }

    public static string DebugRow(long id)
    {
        var row = CachedReportStore.Instance.FetchOne(
            $"SELECT * FROM reports WHERE id = {id}");
        return row is null ? string.Empty : Export.FormatRow(row);
    }

    public static void ClearCache() => PageCache.Clear();
}
