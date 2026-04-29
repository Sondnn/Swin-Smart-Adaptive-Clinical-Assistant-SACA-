using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SACA.WindowsApp.Models
{
    public class TriageRequest
    {
        public string Language { get; set; } = "English";
        public string Gender { get; set; } = "";
        public string PregnancyStatus { get; set; } = "";
        public string AgeGroup { get; set; } = "";
        public List<string> Symptoms { get; set; } = new();
        public string Severity { get; set; } = "";
        public string Duration { get; set; } = "";
        public string Description { get; set; } = "";
        public string AudioRecordingPath { get; set; } = "";
        public string Source { get; set; } = "WindowsApp";
    }
}
