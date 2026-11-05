using System.ComponentModel.DataAnnotations;
using System.Net;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://127.0.0.1:5080");
builder.WebHost.ConfigureKestrel(options => options.Limits.MaxRequestBodySize = 256_000);
builder.Services.ConfigureHttpJsonOptions(options => options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower);
var dataDir = Environment.GetEnvironmentVariable("CONFEREANTES_API_DATA_DIR")
    ?? Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "ConfereAntes", "api");
Directory.CreateDirectory(dataDir);
builder.Services.AddDbContext<HistoryDb>(options => options.UseSqlite($"Data Source={Path.Combine(dataDir, "historico.db")}"));
builder.Services.AddDataProtection().SetApplicationName("ConfereAntes.Api")
    .PersistKeysToFileSystem(new DirectoryInfo(Path.Combine(dataDir, "keys")));
builder.Services.AddHttpClient("processor", client => {
    client.BaseAddress = new Uri("http://127.0.0.1:8000");
    client.Timeout = TimeSpan.FromSeconds(200);
}).ConfigurePrimaryHttpMessageHandler(() => new HttpClientHandler { UseProxy = false, AllowAutoRedirect = false });
var app = builder.Build();
var token = Environment.GetEnvironmentVariable("CONFEREANTES_SERVICE_TOKEN");
if (string.IsNullOrWhiteSpace(token) || token.Length < 32)
    throw new InvalidOperationException("Defina um token interno de pelo menos 32 caracteres pelo iniciador completo.");
using (var scope = app.Services.CreateScope())
    scope.ServiceProvider.GetRequiredService<HistoryDb>().Database.EnsureCreated();

app.Use(async (context, next) => {
    context.Response.Headers.CacheControl = "no-store";
    context.Response.Headers.XContentTypeOptions = "nosniff";
    if (context.Connection.RemoteIpAddress is { } address && !IPAddress.IsLoopback(address)) {
        context.Response.StatusCode = 403;
        return;
    }
    if (context.Request.Path != "/saude") {
        var supplied = context.Request.Headers["X-ConfereAntes-Token"].ToString();
        if (!CryptographicOperations.FixedTimeEquals(Encoding.UTF8.GetBytes(supplied), Encoding.UTF8.GetBytes(token))) {
            context.Response.StatusCode = 401;
            return;
        }
    }
    await next(context);
});
app.MapGet("/saude", () => Results.Ok(new { status = "ok", storage = "EF Core / SQLite" }));
app.MapPost("/analises", async (AnalysisRequest input, IHttpClientFactory factory, HistoryDb db, IDataProtectionProvider protection, CancellationToken cancellation) => {
    var validation = new List<ValidationResult>();
    if (!Validator.TryValidateObject(input, new ValidationContext(input), validation, true))
        return Results.BadRequest(new { error = "Campos excedem os limites permitidos." });
    if (string.IsNullOrWhiteSpace(input.OriginalText) && string.IsNullOrWhiteSpace(input.ReceivedText)
        && string.IsNullOrWhiteSpace(input.Link) && string.IsNullOrWhiteSpace(input.Pix))
        return Results.BadRequest(new { error = "Informe pelo menos uma evidência." });
    try {
        using var request = new HttpRequestMessage(HttpMethod.Post, "/api/analisar");
        request.Headers.Add("X-ConfereAntes-Token", token);
        request.Content = JsonContent.Create(input, options: JsonSettings.Options);
        using var response = await factory.CreateClient("processor").SendAsync(request, cancellation);
        if (!response.IsSuccessStatusCode) return Results.Problem("O processador local rejeitou a análise.", statusCode: 502);
        var result = await response.Content.ReadFromJsonAsync<JsonElement>(JsonSettings.Options, cancellation);
        if (input.SaveHistory) {
            var payload = new {
                score = result.GetProperty("score").GetInt32(),
                level = result.GetProperty("level").GetString(),
                summary = result.GetProperty("summary").GetString(),
                findings = result.GetProperty("findings"),
                original_excerpt = Excerpt(input.OriginalText),
                received_excerpt = Excerpt(input.ReceivedText)
            };
            db.Analyses.Add(new StoredAnalysis {
                CreatedAt = DateTimeOffset.UtcNow,
                ProtectedPayload = protection.CreateProtector("analysis-v1").Protect(JsonSerializer.Serialize(payload, JsonSettings.Options))
            });
            await db.SaveChangesAsync(cancellation);
        }
        return Results.Json(result);
    } catch (Exception exception) when (exception is HttpRequestException or TaskCanceledException) {
        return Results.Problem("Processador Python indisponível. Inicie o modo completo.", statusCode: 503);
    }
});
app.MapGet("/historico", async (HistoryDb db, IDataProtectionProvider protection) => {
    var rows = await db.Analyses.AsNoTracking().OrderByDescending(row => row.Id).Take(30).ToListAsync();
    var entries = new List<object>();
    foreach (var row in rows) {
        try {
            var json = protection.CreateProtector("analysis-v1").Unprotect(row.ProtectedPayload);
            var payload = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json)!;
            payload["id"] = JsonSerializer.SerializeToElement(row.Id);
            payload["created_at"] = JsonSerializer.SerializeToElement(row.CreatedAt);
            entries.Add(payload);
        } catch (CryptographicException) { /* Não expõe conteúdo quando a chave não confere. */ }
    }
    return Results.Ok(entries);
});
app.MapDelete("/historico", async (HistoryDb db) => {
    await db.Analyses.ExecuteDeleteAsync();
    return Results.NoContent();
});
app.Run();

static string Excerpt(string text) {
    var compact = string.Join(' ', text.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries));
    return compact.Length <= 180 ? compact : compact[..179] + "…";
}

public record AnalysisRequest(
    [property: Required(AllowEmptyStrings = true), MaxLength(30000)] string OriginalText = "",
    [property: Required(AllowEmptyStrings = true), MaxLength(30000)] string ReceivedText = "",
    [property: Required(AllowEmptyStrings = true), MaxLength(2000)] string Link = "",
    [property: Required(AllowEmptyStrings = true), MaxLength(2000)] string Pix = "",
    [property: Required(AllowEmptyStrings = true), MaxLength(2000)] string ExpectedRecipient = "",
    [property: Required(AllowEmptyStrings = true), MaxLength(2000)] string DisplayedRecipient = "",
    bool SaveHistory = false,
    bool Explain = false);

public sealed class StoredAnalysis {
    public int Id { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public string ProtectedPayload { get; set; } = "";
}
public sealed class HistoryDb(DbContextOptions<HistoryDb> options) : DbContext(options) {
    public DbSet<StoredAnalysis> Analyses => Set<StoredAnalysis>();
}
public static class JsonSettings {
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web) {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
    };
}
public partial class Program { }
