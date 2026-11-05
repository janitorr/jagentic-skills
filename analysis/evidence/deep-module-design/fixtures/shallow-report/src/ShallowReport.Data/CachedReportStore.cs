namespace ShallowReport.Data;

public sealed class CachedReportStore : ReportStore
{
    private static readonly Dictionary<string, IReadOnlyList<Dictionary<string, object?>>> Cache =
        new(StringComparer.Ordinal);

    private static CachedReportStore? _instance;

    private CachedReportStore()
    {
    }

    public static CachedReportStore Instance => _instance ??= new CachedReportStore();

    public override IReadOnlyList<Dictionary<string, object?>> FetchAll(string sql)
    {
        if (!Cache.TryGetValue(sql, out var rows))
        {
            rows = base.FetchAll(sql);
            Cache[sql] = rows;
        }

        return rows;
    }

    public static void ClearCache() => Cache.Clear();

    public static void ResetForTests(string connectionString)
    {
        _instance?.Dispose();
        _instance = null;
        ClearCache();
        ConnectionString = connectionString;
    }
}
