using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace SACA.WindowsApp.Models
{
    public class TriageResponse
    {
        [JsonPropertyName("triage_category")]
        public int TriageCategory { get; set; }

        [JsonPropertyName("triage_label")]
        public string TriageLabel { get; set; } = "";

        [JsonPropertyName("confidence")]
        public double Confidence { get; set; }

        [JsonPropertyName("probabilities")]
        public Dictionary<string, double> Probabilities { get; set; } = new();

        [JsonPropertyName("model_used")]
        public string ModelUsed { get; set; } = "";

        [JsonPropertyName("disease")]
        public DiseasePrediction? Disease { get; set; }

        [JsonPropertyName("input_summary")]
        public PredictInputSummary InputSummary { get; set; } = new();

        public List<string> Summary { get; set; } = new();
    }

    public class DiseasePrediction
    {
        [JsonPropertyName("disease")]
        public string Disease { get; set; } = "";

        [JsonPropertyName("confidence")]
        public double Confidence { get; set; }

        [JsonPropertyName("top_k")]
        public List<Dictionary<string, object>> TopK { get; set; } = new();
    }

    public class PredictInputSummary
    {
        [JsonPropertyName("gender")]
        public int Gender { get; set; }

        [JsonPropertyName("age_over_65")]
        public int AgeOver65 { get; set; }

        [JsonPropertyName("symptom_severity")]
        public int SymptomSeverity { get; set; }

        [JsonPropertyName("symptoms_duration")]
        public int SymptomsDuration { get; set; }

        [JsonPropertyName("symptoms")]
        public List<string> Symptoms { get; set; } = new();

        [JsonPropertyName("chronic_conditions")]
        public List<string> ChronicConditions { get; set; } = new();

        [JsonPropertyName("escalation_triggers")]
        public List<string> EscalationTriggers { get; set; } = new();

        [JsonPropertyName("had_symptoms_before")]
        public int HadSymptomsBefore { get; set; }

        [JsonPropertyName("had_contact")]
        public int HadContact { get; set; }
    }
}
