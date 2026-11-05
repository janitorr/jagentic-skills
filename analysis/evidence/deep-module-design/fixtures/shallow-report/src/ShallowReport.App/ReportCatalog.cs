using ShallowReport.Data;

namespace ShallowReport.App;

public static class ReportCatalog
{
    public static ReportDto? GetById(long id)
    {
        var sql = $"SELECT id, title, total FROM reports WHERE id = {id}";
        var row = CachedReportStore.Instance.FetchOne(sql);
        return row is null
            ? null
            : new ReportDto(
                (long)row["id"]!,
                (string)row["title"]!,
                (double)row["total"]!);
    }

    public static IReadOnlyList<ReportDto> Search(string titleFragment, double minTotal)
    {
        var sql =
            "SELECT id, title, total FROM reports " +
            $"WHERE title LIKE '%{titleFragment}%' AND total >= {minTotal} ORDER BY id";
        using var command = CachedReportStore.Instance.Connection.CreateCommand();
        command.CommandText = sql;
        using var reader = command.ExecuteReader();
        var results = new List<ReportDto>();
        while (reader.Read())
        {
            results.Add(new ReportDto(
                reader.GetInt64(0),
                reader.GetString(1),
                reader.GetDouble(2)));
        }

        return results;
    }
}
