using System.Net;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.DependencyInjection.Extensions;
using Xunit;

public class ApiTests {
    [Fact]
    public async Task EnforcesTokenAndStoresEncryptedHistoryOnlyWhenRequested() {
        var dataDir = Path.Combine(Path.GetTempPath(), "ConfereAntes.Tests", Guid.NewGuid().ToString("N"));
        Environment.SetEnvironmentVariable("CONFEREANTES_API_DATA_DIR", dataDir);
        Environment.SetEnvironmentVariable("CONFEREANTES_SERVICE_TOKEN", new string('t', 64));
        using var factory = new TestApi();
        using var client = factory.CreateClient();
        Assert.Equal(HttpStatusCode.Unauthorized, (await client.GetAsync("/historico")).StatusCode);
        Assert.Equal(HttpStatusCode.Unauthorized, (await client.DeleteAsync("/historico")).StatusCode);
        client.DefaultRequestHeaders.Add("X-ConfereAntes-Token", new string('t', 64));
        var input = new { received_text = "EVIDENCIA PRIVADA DE TESTE", save_history = false };
        Assert.Equal(HttpStatusCode.OK, (await client.PostAsJsonAsync("/analises", input)).StatusCode);
        Assert.Empty((await client.GetFromJsonAsync<JsonElement[]>("/historico"))!);
        var saved = await client.PostAsJsonAsync("/analises", new { received_text = input.received_text, save_history = true });
        Assert.Equal(HttpStatusCode.OK, saved.StatusCode);
        var entries = await client.GetFromJsonAsync<JsonElement[]>("/historico");
        Assert.Single(entries!);
        Assert.Equal(input.received_text, entries![0].GetProperty("received_excerpt").GetString());
        using var dbStream = new FileStream(Path.Combine(dataDir, "historico.db"), FileMode.Open, FileAccess.Read, FileShare.ReadWrite);
        using var dbReader = new StreamReader(dbStream);
        var raw = await dbReader.ReadToEndAsync();
        Assert.DoesNotContain(input.received_text, raw);
        Assert.Equal(HttpStatusCode.NoContent, (await client.DeleteAsync("/historico")).StatusCode);
        Assert.Empty((await client.GetFromJsonAsync<JsonElement[]>("/historico"))!);
        Assert.Equal(HttpStatusCode.BadRequest, (await client.PostAsJsonAsync("/analises", new { received_text = new string('x', 30001) })).StatusCode);
        Assert.Equal(HttpStatusCode.BadRequest, (await client.PostAsJsonAsync("/analises", new { })).StatusCode);
    }
}

public class TestApi : WebApplicationFactory<Program> {
    protected override void ConfigureWebHost(IWebHostBuilder builder) {
        builder.ConfigureServices(services => {
            services.RemoveAll<IHttpClientFactory>();
            services.AddSingleton<IHttpClientFactory, FakeProcessorFactory>();
        });
    }
}
public class FakeProcessorFactory : IHttpClientFactory {
    public HttpClient CreateClient(string name) => new(new FakeProcessor()) { BaseAddress = new Uri("http://127.0.0.1:8000") };
}
public class FakeProcessor : HttpMessageHandler {
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) {
        Assert.True(request.Headers.Contains("X-ConfereAntes-Token"));
        return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK) {
            Content = JsonContent.Create(new { score = 40, level = "atencao", summary = "Confirme por outro canal.", findings = Array.Empty<object>() })
        });
    }
}
