using SACA.WindowsApp.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Net.Http.Json;
using System.Text.Json;

namespace SACA.WindowsApp.Services
{
    public class TriageApiService
    {
        private readonly HttpClient _httpClient;

        // Change this later when backend teammate gives the real URL
        private const string ApiUrl = "http://localhost:8000/api/triage/analyse";
        private const string SpeechToTextUrl = "http://127.0.0.1:8000/speech-to-text";
        private const string SpeechToTextPageUrl = "http://127.0.0.1:8000/speech-to-text-page";

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

        public async Task<string> ConvertSpeechToTextAsync(string audioFilePath, int languageCode)
        {
            if (!File.Exists(audioFilePath))
            {
                throw new FileNotFoundException("The voice recording file could not be found.", audioFilePath);
            }

            using var form = new MultipartFormDataContent();
            form.Add(new StringContent(languageCode.ToString()), "language");

            await using var fileStream = File.OpenRead(audioFilePath);
            using var fileContent = new StreamContent(fileStream);
            fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
            form.Add(fileContent, "files", Path.GetFileName(audioFilePath));

            using HttpResponseMessage response = await _httpClient.PostAsync(SpeechToTextUrl, form);

            if (!response.IsSuccessStatusCode)
            {
                string errorBody = await response.Content.ReadAsStringAsync();
                throw new Exception($"Unable to convert speech to text. Server returned {(int)response.StatusCode}: {errorBody}");
            }

            string responseBody = await response.Content.ReadAsStringAsync();
            return ExtractTranscript(responseBody);
        }

        public async Task<SpeechToTextPageResult> ConvertSpeechToTextPageAsync(string audioFilePath, int languageCode, int questionId)
        {
            if (!File.Exists(audioFilePath))
            {
                throw new FileNotFoundException("The voice recording file could not be found.", audioFilePath);
            }

            using var form = new MultipartFormDataContent();
            form.Add(new StringContent(languageCode.ToString()), "language");
            form.Add(new StringContent(questionId.ToString()), "question_id");

            await using var fileStream = File.OpenRead(audioFilePath);
            using var fileContent = new StreamContent(fileStream);
            fileContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("audio/wav");
            form.Add(fileContent, "files", Path.GetFileName(audioFilePath));

            using HttpResponseMessage response = await _httpClient.PostAsync(SpeechToTextPageUrl, form);
            string responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception($"Unable to process voice answer. Server returned {(int)response.StatusCode}: {responseBody}");
            }

            using JsonDocument document = JsonDocument.Parse(responseBody);
            JsonElement root = document.RootElement;

            if (root.TryGetProperty("error", out JsonElement error))
            {
                throw new Exception(error.GetString() ?? "The speech-to-text service returned an error.");
            }

            if (!root.TryGetProperty("parsed_response", out JsonElement parsedResponse)
                || parsedResponse.ValueKind == JsonValueKind.Null
                || parsedResponse.ValueKind == JsonValueKind.Undefined)
            {
                throw new Exception($"The voice answer could not be understood for this question. Response: {responseBody}");
            }

            int returnedQuestionId = questionId;

            if (root.TryGetProperty("question_id", out JsonElement returnedQuestion)
                && returnedQuestion.ValueKind == JsonValueKind.Number
                && returnedQuestion.TryGetInt32(out int parsedQuestionId))
            {
                returnedQuestionId = parsedQuestionId;
            }

            JsonElement parsedClone = parsedResponse.Clone();
            string parsedJson = parsedClone.GetRawText();

            return new SpeechToTextPageResult
            {
                QuestionId = returnedQuestionId,
                ParsedResponse = parsedClone,
                ParsedResponseJson = parsedJson,
                DisplayText = ToDisplayText(parsedClone)
            };
        }

        private static string ToDisplayText(JsonElement element)
        {
            return element.ValueKind switch
            {
                JsonValueKind.String => element.GetString() ?? "",
                JsonValueKind.Number => element.GetRawText(),
                JsonValueKind.True => "Yes",
                JsonValueKind.False => "No",
                JsonValueKind.Array => string.Join(", ", element.EnumerateArray().Select(ToDisplayText).Where(value => !string.IsNullOrWhiteSpace(value))),
                JsonValueKind.Object => string.Join(", ", element.EnumerateObject().Select(property => $"{property.Name}: {ToDisplayText(property.Value)}")),
                _ => element.GetRawText()
            };
        }

        private static string ExtractTranscript(string responseBody)
        {
            using JsonDocument document = JsonDocument.Parse(responseBody);
            string? transcript = FindTranscript(document.RootElement);

            if (!string.IsNullOrWhiteSpace(transcript))
            {
                return transcript;
            }
            throw new Exception($"The speech-to-text response did not include a recognised text field. Response: {responseBody}");
        }

        private static string? FindTranscript(JsonElement element)
        {
            if (element.ValueKind == JsonValueKind.String)
            {
                return element.GetString();
            }

            if (element.ValueKind == JsonValueKind.Object)
            {
                foreach (JsonProperty property in element.EnumerateObject())
                {
                    if (property.Value.ValueKind == JsonValueKind.String && IsTranscriptField(property.Name))
                    {
                        return property.Value.GetString();
                    }
                }

                foreach (JsonProperty property in element.EnumerateObject())
                {
                    string? nestedValue = FindTranscript(property.Value);

                    if (!string.IsNullOrWhiteSpace(nestedValue))
                    {
                        return nestedValue;
                    }
                }
            }

            if (element.ValueKind == JsonValueKind.Array)
            {
                foreach (JsonElement item in element.EnumerateArray())
                {
                    string? nestedValue = FindTranscript(item);

                    if (!string.IsNullOrWhiteSpace(nestedValue))
                    {
                        return nestedValue;
                    }
                }
            }

            return null;
        }

        private static bool IsTranscriptField(string fieldName)
        {
            string normalisedFieldName = fieldName.Replace("_", "", StringComparison.OrdinalIgnoreCase)
                .Replace("-", "", StringComparison.OrdinalIgnoreCase)
                .Replace(" ", "", StringComparison.OrdinalIgnoreCase);

            return normalisedFieldName.Contains("symptomsdescription", StringComparison.OrdinalIgnoreCase)
                || normalisedFieldName.Contains("description", StringComparison.OrdinalIgnoreCase)
                || normalisedFieldName.Contains("text", StringComparison.OrdinalIgnoreCase)
                || normalisedFieldName.Contains("transcript", StringComparison.OrdinalIgnoreCase)
                || normalisedFieldName.Contains("transcription", StringComparison.OrdinalIgnoreCase)
                || normalisedFieldName.Contains("result", StringComparison.OrdinalIgnoreCase)
                || normalisedFieldName.Contains("result", StringComparison.OrdinalIgnoreCase);
        }
    }
}
