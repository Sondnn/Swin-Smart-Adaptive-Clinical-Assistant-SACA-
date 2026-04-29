using SACA.WindowsApp.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Net.Http.Json;

namespace SACA.WindowsApp.Services
{
    public class TriageApiService
    {
        private readonly HttpClient _httpClient;

        // Change this later when backend teammate gives the real URL
        private const string ApiUrl = "http://localhost:8000/api/triage/analyse";

        public TriageApiService()
        {
            _httpClient = new HttpClient();
        }

        public async Task<TriageResponse> AnalyseAsync(TriageRequest request)
        {
            // Use mock first for Week 1 demo
            bool useMock = true;

            if (useMock)
            {
                await Task.Delay(1000);

                return new TriageResponse
                {
                    TriageLevel = "Semi-urgent",
                    Recommendation = "Please contact the clinic for an appointment and monitor symptoms closely.",
                    Confidence = 0.82,
                    Summary = request.Symptoms
                };
            }

            var response = await _httpClient.PostAsJsonAsync(ApiUrl, request);

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception("Unable to receive triage result from the server.");
            }

            var result = await response.Content.ReadFromJsonAsync<TriageResponse>();

            return result ?? throw new Exception("Empty response from server.");
        }
    }
}