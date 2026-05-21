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
        private const string PredictUrl = "http://127.0.0.1:8000/predict";
        private const string SpeechToTextUrl = "http://127.0.0.1:8000/speech-to-text";
        private const string SpeechToTextPageUrl = "http://127.0.0.1:8000/speech-to-text-page";

        public TriageApiService()
        {
            _httpClient = new HttpClient();
        }

        public async Task<TriageResponse> AnalyseAsync(TriageRequest request)
        {
            var predictRequest = BuildPredictRequest(request);
            HttpResponseMessage response;

            try
            {
                response = await _httpClient.PostAsJsonAsync(PredictUrl, predictRequest);
            }
            catch (HttpRequestException)
            {
                throw new Exception("We could not connect to the assessment service. Please check that the service is running and try again.");
            }
            catch (TaskCanceledException)
            {
                throw new Exception("The assessment service took too long to respond. Please try again.");
            }

            if (!response.IsSuccessStatusCode)
            {
                string errorBody = await response.Content.ReadAsStringAsync();
                throw new Exception(ToFriendlyBackendMessage(errorBody, "assessment"));
            }

            var result = await response.Content.ReadFromJsonAsync<TriageResponse>();

            if (result == null)
            {
                throw new Exception("Empty response from server.");
            }

            result.Summary = result.InputSummary.Symptoms.Any()
                ? result.InputSummary.Symptoms
                : request.Symptoms;

            return result;
        }

        private static object BuildPredictRequest(TriageRequest request)
        {
            List<string> symptoms = request.Symptoms.Select(ToBackendToken).Where(value => !string.IsNullOrWhiteSpace(value)).Distinct().ToList();
            List<string> chronicConditions = request.ChronicConditions
                .Where(value => !value.Contains("Unknown", StringComparison.OrdinalIgnoreCase))
                .Select(MapChronicCondition)
                .Where(value => !string.IsNullOrWhiteSpace(value))
                .Distinct()
                .ToList();

            List<string> escalationTriggers = symptoms
                .Where(symptom => symptom is "chest_pain" or "breathing_difficulty")
                .ToList();

            return new
            {
                gender = MapGender(request.Gender),
                age_over_65 = MapAgeOver65(request.AgeGroup),
                symptom_severity = MapSeverity(request.Severity),
                symptoms_duration = MapDuration(request.Duration),
                symptoms,
                chronic_conditions = chronicConditions,
                escalation_triggers = escalationTriggers,
                had_symptoms_before = MapTriState(request.HadSymptomsBefore),
                had_contact = MapTriState(request.RecentSickContact)
            };
        }

        private static int MapGender(string value)
        {
            if (value.Equals("Female", StringComparison.OrdinalIgnoreCase))
            {
                return 0;
            }

            if (value.Equals("Male", StringComparison.OrdinalIgnoreCase))
            {
                return 1;
            }

            return 2;
        }

        private static int MapAgeOver65(string value)
        {
            if (value.Contains("Older", StringComparison.OrdinalIgnoreCase))
            {
                return 1;
            }

            if (value.Contains("65", StringComparison.OrdinalIgnoreCase))
            {
                return 0;
            }

            return 2;
        }

        private static int MapSeverity(string value)
        {
            string normalisedValue = value.Trim().ToLowerInvariant();

            if (int.TryParse(normalisedValue, out int severityCode) && severityCode >= 1 && severityCode <= 5)
            {
                return severityCode;
            }

            return normalisedValue switch
            {
                "mild" => 1,
                "low" => 2,
                "moderate" => 3,
                "high" => 4,
                "severe" => 5,
                _ => 3
            };
        }

        private static int MapDuration(string value)
        {
            if (int.TryParse(value.Trim(), out int durationCode) && durationCode >= 0 && durationCode <= 2)
            {
                return durationCode;
            }

            if (value.Contains("less", StringComparison.OrdinalIgnoreCase)
                || value.Contains("under", StringComparison.OrdinalIgnoreCase)
                || value.Contains("shorter", StringComparison.OrdinalIgnoreCase)
                || value.Contains("fewer", StringComparison.OrdinalIgnoreCase))
            {
                return 0;
            }

            if (value.Contains("more", StringComparison.OrdinalIgnoreCase)
                || value.Contains("over", StringComparison.OrdinalIgnoreCase)
                || value.Contains("longer", StringComparison.OrdinalIgnoreCase)
                || value.Contains("greater", StringComparison.OrdinalIgnoreCase))
            {
                return 1;
            }

            if (value.Contains("unknown", StringComparison.OrdinalIgnoreCase)
                || value.Contains("don't know", StringComparison.OrdinalIgnoreCase)
                || value.Contains("not sure", StringComparison.OrdinalIgnoreCase))
            {
                return 2;
            }

            return 2;
        }

        private static int MapTriState(string value)
        {
            if (value.Equals("Yes", StringComparison.OrdinalIgnoreCase))
            {
                return 1;
            }

            if (value.Equals("No", StringComparison.OrdinalIgnoreCase))
            {
                return 0;
            }

            return 2;
        }

        private static string ToBackendToken(string value)
        {
            return value.Trim()
                .ToLowerInvariant()
                .Replace("-", "_")
                .Replace("/", "_")
                .Replace(" ", "_")
                .Replace("__", "_");
        }

        private static string MapChronicCondition(string value)
        {
            string normalisedValue = ToBackendToken(value);

            return normalisedValue switch
            {
                "type_2_diabetes" => "type2_diabetes",
                "asthma_copd" => "asthma_copd",
                "depression_anxiety" => "depression_anxiety",
                "heart_disease" => "heart_disease",
                "hypertension" => "hypertension",
                _ => normalisedValue
            };
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

            using HttpResponseMessage response = await PostVoiceRequestAsync(SpeechToTextUrl, form);

            if (!response.IsSuccessStatusCode)
            {
                string errorBody = await response.Content.ReadAsStringAsync();
                throw new Exception(ToFriendlyBackendMessage(errorBody, "voice"));
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

            using HttpResponseMessage response = await PostVoiceRequestAsync(SpeechToTextPageUrl, form);
            string responseBody = await response.Content.ReadAsStringAsync();

            if (!response.IsSuccessStatusCode)
            {
                throw new Exception(ToFriendlyBackendMessage(responseBody, "voice"));
            }

            using JsonDocument document = JsonDocument.Parse(responseBody);
            JsonElement root = document.RootElement;

            if (root.TryGetProperty("error", out JsonElement error))
            {
                throw new Exception(ToFriendlyBackendMessage(error.GetString() ?? responseBody, "voice"));
            }

            if (!root.TryGetProperty("parsed_response", out JsonElement parsedResponse)
                || parsedResponse.ValueKind == JsonValueKind.Null
                || parsedResponse.ValueKind == JsonValueKind.Undefined)
            {
                throw new Exception(ToFriendlyBackendMessage(responseBody, "voice"));
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

        private async Task<HttpResponseMessage> PostVoiceRequestAsync(string url, MultipartFormDataContent form)
        {
            try
            {
                return await _httpClient.PostAsync(url, form);
            }
            catch (HttpRequestException)
            {
                throw new Exception("We could not connect to the voice service. Please check that the service is running and try again.");
            }
            catch (TaskCanceledException)
            {
                throw new Exception("The voice service took too long to respond. Please try again.");
            }
        }

        private static string ToFriendlyBackendMessage(string responseBody, string context)
        {
            string backendMessage = ExtractBackendMessage(responseBody);
            string normalisedMessage = backendMessage.ToLowerInvariant();

            if (context == "voice")
            {
                if (normalisedMessage.Contains("audio")
                    || normalisedMessage.Contains("speech")
                    || normalisedMessage.Contains("silent")
                    || normalisedMessage.Contains("noise")
                    || normalisedMessage.Contains("understand")
                    || normalisedMessage.Contains("transcrib")
                    || normalisedMessage.Contains("empty")
                    || normalisedMessage.Contains("too short")
                    || normalisedMessage.Contains("quality"))
                {
                    return "We could not understand the recording. Please try again in a quiet place and speak clearly.";
                }

                return "We could not process the voice answer. Please try recording it again.";
            }

            return "We could not complete the assessment right now. Please check your answers and try again.";
        }

        private static string ExtractBackendMessage(string responseBody)
        {
            if (string.IsNullOrWhiteSpace(responseBody))
            {
                return "";
            }

            try
            {
                using JsonDocument document = JsonDocument.Parse(responseBody);
                string? message = FindBackendMessage(document.RootElement);
                return string.IsNullOrWhiteSpace(message) ? responseBody : message;
            }
            catch (JsonException)
            {
                return responseBody;
            }
        }

        private static string? FindBackendMessage(JsonElement element)
        {
            if (element.ValueKind == JsonValueKind.String)
            {
                return element.GetString();
            }

            if (element.ValueKind == JsonValueKind.Object)
            {
                foreach (string propertyName in new[] { "message", "error", "detail", "description" })
                {
                    if (element.TryGetProperty(propertyName, out JsonElement propertyValue))
                    {
                        string? value = FindBackendMessage(propertyValue);

                        if (!string.IsNullOrWhiteSpace(value))
                        {
                            return value;
                        }
                    }
                }

                foreach (JsonProperty property in element.EnumerateObject())
                {
                    string? value = FindBackendMessage(property.Value);

                    if (!string.IsNullOrWhiteSpace(value))
                    {
                        return value;
                    }
                }
            }

            if (element.ValueKind == JsonValueKind.Array)
            {
                foreach (JsonElement item in element.EnumerateArray())
                {
                    string? value = FindBackendMessage(item);

                    if (!string.IsNullOrWhiteSpace(value))
                    {
                        return value;
                    }
                }
            }

            return null;
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
