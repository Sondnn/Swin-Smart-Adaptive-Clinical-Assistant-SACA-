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

            SeverityLabelTextBlock.Text = response.TriageLabel;
            SeverityIconImage.Source = new BitmapImage(new Uri(GetSeverityIconPath(response.TriageLabel), UriKind.Relative));
            RecommendationBodyTextBlock.Text = GetRecommendation(response.TriageLabel);

            List<string> symptoms = response.Summary.Any()
                ? response.Summary
                : response.InputSummary.Symptoms;

            SummaryTextBlock.Text = symptoms.Any()
                ? string.Join(", ", symptoms.Select(ToDisplayText))
                : "No symptoms were provided.";

            DiagnosticTextBlock.Text = string.IsNullOrWhiteSpace(response.Disease?.Disease)
                ? "A likely diagnostic condition was not returned by the model."
                : $"You are likely to have {response.Disease.Disease}.";
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
                "Immediate" => "/Assets/Icons/severity_category_A.png",
                "Emergency" => "/Assets/Icons/severity_category_B.png",
                "Urgent" => "/Assets/Icons/severity_category_C.png",
                "Semi-Urgent" => "/Assets/Icons/severity_category_D.png",
                "Non-Urgent" => "/Assets/Icons/severity_category_E.png",
                "Referred" => "/Assets/Icons/severity_category_F.png",
                _ => "/Assets/Icons/severity_category_D.png"
            };
        }

        private static string GetRecommendation(string triageLabel)
        {
            return triageLabel switch
            {
                "Immediate" => "Seek immediate medical care now. Call emergency services or attend the nearest emergency department.",
                "Emergency" => "Attend the emergency department as soon as possible for urgent medical assessment.",
                "Urgent" => "Contact a clinic or healthcare professional urgently today for assessment and advice.",
                "Semi-Urgent" => "Arrange a medical appointment soon and monitor your symptoms closely.",
                "Non-Urgent" => "Monitor your symptoms, rest, and book a routine appointment if symptoms continue or worsen.",
                "Referred" => "A healthcare professional should review your symptoms and direct you to the most appropriate service.",
                _ => "Please speak with a healthcare professional for further assessment."
            };
        }

        private static string ToDisplayText(string value)
        {
            return string.Join(
                " ",
                value.Replace("_", " ")
                    .Split(' ', StringSplitOptions.RemoveEmptyEntries)
                    .Select(word => char.ToUpperInvariant(word[0]) + word[1..]));
        }
    }
}
