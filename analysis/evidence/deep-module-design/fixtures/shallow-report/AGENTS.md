# Shallow Report

- .NET 10, C#; `Microsoft.Data.Sqlite`.
- Keep behavior; do not add features.
- `src/ShallowReport.Data` is the only project that touches the database.
- Reads go through `CachedReportStore.Instance`; writes go through `Ingest`,
  which clears the cache.
- A batch import is all-or-nothing, and a duplicate id fails.
- Run tests with `dotnet run --project tests/ShallowReport.Tests`.
