using Microsoft.Data.Sqlite;

namespace ShallowReport.Data;

public class ReportStore : IDisposable
{
    public static string ConnectionString { get; set; } = "Data Source=shallow-report.db";

    private readonly SqliteConnection _connection;

    protected ReportStore()
    {
        _connection = new SqliteConnection(ConnectionString);
        _connection.Open();
    }

    public SqliteConnection Connection => _connection;

    public virtual IReadOnlyList<Dictionary<string, object?>> FetchAll(string sql)
    {
        using var command = _connection.CreateCommand();
        command.CommandText = sql;
        using var reader = command.ExecuteReader();
        var rows = new List<Dictionary<string, object?>>();
        while (reader.Read())
        {
            var row = new Dictionary<string, object?>(StringComparer.Ordinal);
            for (var i = 0; i < reader.FieldCount; i++)
            {
                row[reader.GetName(i)] = reader.IsDBNull(i) ? null : reader.GetValue(i);
            }

            rows.Add(row);
        }

        return rows;
    }

    public Dictionary<string, object?>? FetchOne(string sql)
    {
        var rows = FetchAll(sql);
        return rows.Count == 0 ? null : rows[0];
    }

    public int Execute(string sql)
    {
        using var command = _connection.CreateCommand();
        command.CommandText = sql;
        return command.ExecuteNonQuery();
    }

    public IReadOnlyList<string> Columns(string table = "reports")
    {
        using var command = _connection.CreateCommand();
        command.CommandText = $"PRAGMA table_info({table})";
        using var reader = command.ExecuteReader();
        var columns = new List<string>();
        while (reader.Read())
        {
            columns.Add(reader.GetString(1));
        }

        return columns;
    }

    public string TableName() => "reports";

    public void Dispose() => _connection.Dispose();
}
