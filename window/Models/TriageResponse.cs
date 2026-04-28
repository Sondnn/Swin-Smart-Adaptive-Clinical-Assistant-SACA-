using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SACA.WindowsApp.Models
{
    public class TriageResponse
    {
        public string TriageLevel { get; set; } = "";
        public string Recommendation { get; set; } = "";
        public double Confidence { get; set; }
        public List<string> Summary { get; set; } = new();
    }
}
