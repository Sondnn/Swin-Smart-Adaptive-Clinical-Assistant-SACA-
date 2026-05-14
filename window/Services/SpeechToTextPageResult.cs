using System.Text.Json;

namespace SACA.WindowsApp.Services
{
    public class SpeechToTextPageResult
    {
        public int QuestionId { get; set; }
        public JsonElement ParsedResponse { get; set; }
        public string ParsedResponseJson { get; set; } = "";
        public string DisplayText { get; set; } = "";
    }
}
