using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using SACA.WindowsApp.Models;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for ResultPage.xaml
    /// </summary>
    public partial class ResultPage : UserControl
    {
        private readonly MainWindow _mainWindow;

        public ResultPage(MainWindow mainWindow, TriageResponse response)
        {
            InitializeComponent();
            _mainWindow = mainWindow;

            SeverityLabelTextBlock.Text = GetDisplayTriageLabel(response.TriageLabel);
            SeverityIconImage.Source = new BitmapImage(new Uri(GetSeverityIconPath(response.TriageLabel), UriKind.Relative));
            RecommendationBodyTextBlock.Text = GetRecommendation(response.TriageLabel);

            List<string> symptoms = response.Summary.Any()
                ? response.Summary
                : response.InputSummary.Symptoms;

            SummaryTextBlock.Text = symptoms.Any()
                ? string.Join(", ", symptoms.Select(ToDisplaySymptom))
                : "No symptoms were provided.";

            DiagnosticTextBlock.Text = string.IsNullOrWhiteSpace(response.Disease?.Disease)
                ? AppLanguage.T("diagnostic_not_returned")
                : $"{AppLanguage.T("diagnostic_likely_prefix")} {ToDisplayDisease(response.Disease.Disease)}.";
        }

        private void StartAgain_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.CurrentRequest = new TriageRequest();
            AppLanguage.SetLanguage("English");
            _mainWindow.NavigateToSplash();
        }

        private void Ok_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private static string GetSeverityIconPath(string triageLabel)
        {
            return triageLabel switch
            {
                "Resuscitation" => "/Assets/Icons/severity_category_A.png",
                "Emergent" => "/Assets/Icons/severity_category_B.png",
                "Urgent" => "/Assets/Icons/severity_category_C.png",
                "Less Urgent" => "/Assets/Icons/severity_category_F.png",
                "Non-Urgent" => "/Assets/Icons/severity_category_E.png",
                _ => "/Assets/Icons/severity_category_D.png"
            };
        }

        private static string GetRecommendation(string triageLabel)
        {
            if (AppLanguage.IsWalmajarri)
            {
                return triageLabel switch
                {
                    "Resuscitation" => "Karlarra-ku yirrarni-rna nyuntu-ju karlarra-wana yirrarni karlarra.",
                    "Emergent" => "Karlarra-ku yirrarni-rna nyuntu-ju karlarra jukurra yirrarni.",
                    "Urgent" => "Karlarra-ku yirrarni-rna nyuntu-ju karlarra yirrarni-wana yimi",
                    "Less Urgent" => "Karlarra-ku yirrarni-rna nyuntu-ju karlarra jukurra yirrarni-wana.",
                    "Non-Urgent" => "Karlarra-ku yirrarni-rna nyuntu-ju karlarra yirrarni kujarra.",
                    _ => "Please speak with a healthcare professional for further assessment."
                };
            }

            return triageLabel switch
            {
                "Resuscitation" => "Patient requires immediate life-saving medical attention. See the doctor or emergency team immediately.",
                "Emergent" => "Patient should be seen urgently by the doctor or emergency department as soon as possible.",
                "Urgent" => "Patient should be assessed by the practice nurse or doctor today. Monitor symptoms closely.",
                "Less Urgent" => "Patient should attend the clinic for assessment and make an appointment today.",
                "Non-Urgent" => "Patient may make a routine appointment and should call back if symptoms worsen.",
                _ => "Please speak with a healthcare professional for further assessment."
            };
        }

        private static string GetDisplayTriageLabel(string triageLabel)
        {
            if (!AppLanguage.IsWalmajarri)
            {
                return triageLabel;
            }

            return triageLabel switch
            {
                "Resuscitation" => "Karlarra Wana",
                "Emergent" => "Karlarra Jukurra",
                "Urgent" => "Yirrarni Wana",
                "Less Urgent" => "Yirrarni Kujarra",
                "Non-Urgent" => "Kujarra",
                _ => triageLabel
            };
        }

        private static string ToDisplaySymptom(string value)
        {
            string normalisedValue = value.Trim()
                .ToLowerInvariant()
                .Replace("-", "_")
                .Replace(" ", "_");

            if (AppLanguage.IsWalmajarri)
            {
                return normalisedValue switch
                {
                    "fever" => "Karlarra Waru",
                    "diarrhea" or "diarrhoea" => "Karlarra Parnta",
                    "cough" => "Karlarra Kurrkurr",
                    "vomiting" => "Karlarra Puka",
                    "dizziness" => "Karlarra Mirrirr",
                    "cold" => "Karlarra Mirrirr",
                    "runny_nose" => "Karlarra Munyju",
                    "eye_pain" => "Karlarra Miji",
                    "sore_throat" => "Karlarra Juwi",
                    "headache" => "Karlarra Kuja",
                    "joint_pain" => "Karlarra Jirrpi",
                    "abdominal_pain" => "Karlarra Jirri",
                    "belly_pain" => "Karlarra Jirri",
                    "body_pain" => "Karlarra Yijiji",
                    _ => ToTitleCase(value)
                };
            }

            return normalisedValue switch
            {
                "diarrhoea" => "Diarrhea",
                "runny_nose" => "Runny Nose",
                "eye_pain" => "Eye Pain",
                "sore_throat" => "Sore throat",
                "joint_pain" => "Joint Pain",
                "abdominal_pain" => "Abdominal Pain",
                "belly_pain" => "Belly pain",
                "body_pain" => "Body Pain",
                _ => ToTitleCase(value)
            };
        }

        private static string ToDisplayDisease(string disease)
        {
            if (!AppLanguage.IsWalmajarri)
            {
                return ToTitleCase(disease);
            }

            string normalisedDisease = NormaliseDiseaseName(disease);

            return WalmajarriDiseaseNames.TryGetValue(normalisedDisease, out string? translatedDisease)
                ? translatedDisease
                : ToTitleCase(disease);
        }

        private static string NormaliseDiseaseName(string value)
        {
            return value.Trim()
                .ToLowerInvariant()
                .Replace("_", " ")
                .Replace("-", " ");
        }

        private static readonly Dictionary<string, string> WalmajarriDiseaseNames = new()
        {
            // Add verified Walmajarri disease names here as they are supplied.
        };

        private static string ToTitleCase(string value)
        {
            return string.Join(
                " ",
                value.Replace("_", " ")
                    .Split(' ', StringSplitOptions.RemoveEmptyEntries)
                    .Select(word => char.ToUpperInvariant(word[0]) + word[1..]));
        }
    }
}
