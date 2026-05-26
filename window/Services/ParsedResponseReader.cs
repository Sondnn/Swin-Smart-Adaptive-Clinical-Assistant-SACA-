using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace SACA.WindowsApp.Services
{
    public static class ParsedResponseReader
    {
        public static string ReadSingleValue(string json)
        {
            using JsonDocument document = JsonDocument.Parse(json);
            return ReadSingleValue(document.RootElement);
        }

        public static List<string> ReadStringList(string json)
        {
            using JsonDocument document = JsonDocument.Parse(json);
            return ReadStringList(document.RootElement);
        }

        private static string ReadSingleValue(JsonElement element)
        {
            if (element.ValueKind == JsonValueKind.String)
            {
                return element.GetString() ?? "";
            }

            if (element.ValueKind == JsonValueKind.Number || element.ValueKind == JsonValueKind.True || element.ValueKind == JsonValueKind.False)
            {
                return element.ToString();
            }

            if (element.ValueKind == JsonValueKind.Array)
            {
                return element.EnumerateArray()
                    .Select(ReadSingleValue)
                    .FirstOrDefault(value => !string.IsNullOrWhiteSpace(value)) ?? "";
            }

            if (element.ValueKind == JsonValueKind.Object)
            {
                string[] preferredFields =
                {
                    "value",
                    "answer",
                    "gender",
                    "age",
                    "age_over_65",
                    "severity",
                    "symptom_severity",
                    "duration",
                    "symptoms_duration",
                    "had_symptoms_before",
                    "had_contact",
                    "response",
                    "result"
                };

                foreach (string field in preferredFields)
                {
                    if (element.TryGetProperty(field, out JsonElement propertyValue))
                    {
                        string value = ReadSingleValue(propertyValue);

                        if (!string.IsNullOrWhiteSpace(value))
                        {
                            return value;
                        }
                    }
                }

                foreach (JsonProperty property in element.EnumerateObject())
                {
                    string value = ReadSingleValue(property.Value);

                    if (!string.IsNullOrWhiteSpace(value))
                    {
                        return value;
                    }
                }
            }

            return "";
        }

        private static List<string> ReadStringList(JsonElement element)
        {
            if (element.ValueKind == JsonValueKind.Array)
            {
                return element.EnumerateArray()
                    .Select(ReadSingleValue)
                    .Where(value => !string.IsNullOrWhiteSpace(value))
                    .ToList();
            }

            if (element.ValueKind == JsonValueKind.Object)
            {
                foreach (JsonProperty property in element.EnumerateObject())
                {
                    if (property.Value.ValueKind == JsonValueKind.Array)
                    {
                        return ReadStringList(property.Value);
                    }
                }

                var truthyKeys = element.EnumerateObject()
                    .Where(property => property.Value.ValueKind == JsonValueKind.True)
                    .Select(property => property.Name)
                    .ToList();

                if (truthyKeys.Any())
                {
                    return truthyKeys;
                }
            }

            string singleValue = ReadSingleValue(element);
            return string.IsNullOrWhiteSpace(singleValue)
                ? new List<string>()
                : new List<string> { singleValue };
        }
    }
}
