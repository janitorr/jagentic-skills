using ShallowReport.Data;

namespace ShallowReport.App;

public static class Summary
{
    public static IReadOnlyDictionary<string, double> TotalsByCategory(string start, string end)
    {
        var rows = CachedReportStore.Instance.FetchAll("SELECT * FROM reports");
        return rows
            .Where(row =>
                string.CompareOrdinal((string)row["created_at"]!, start) >= 0
                && string.CompareOrdinal((string)row["created_at"]!, end) < 0)
            .GroupBy(row => (string)row["category"]!)
            .OrderBy(group => group.Key)
            .ToDictionary(
                group => group.Key,
                group => group.Sum(row => (double)row["total"]!));
    }
}
