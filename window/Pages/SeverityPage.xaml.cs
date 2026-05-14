using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for SeverityPage.xaml
    /// </summary>
    public partial class SeverityPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private string _recordedSeverity = "";

        public SeverityPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            VoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            VoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;

            if (!string.IsNullOrWhiteSpace(_mainWindow.CurrentRequest.Severity))
            {
                SelectSeverity(_mainWindow.CurrentRequest.Severity);
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToSymptoms();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            string severity = GetSelectedSeverity();

            if (string.IsNullOrWhiteSpace(severity))
            {
                severity = _recordedSeverity;
            }

            if (string.IsNullOrWhiteSpace(severity))
            {
                MessageBox.Show("Please select severity level, or answer using voice.");
                return;
            }

            _mainWindow.CurrentRequest.Severity = severity;
            _mainWindow.CurrentRequest.AudioRecordingPath = VoiceRecorder.LastRecordingPath;
            _mainWindow.NavigateToDuration();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _recordedSeverity = MapSeverityResponse(ParsedResponseReader.ReadSingleValue(e.ParsedResponseJson));
            SelectSeverity(_recordedSeverity);
            _mainWindow.CurrentRequest.AudioRecordingPath = e.RecordingPath;
            _mainWindow.CurrentRequest.AudioRecordingPaths.Add(e.RecordingPath);
            _mainWindow.CurrentRequest.VoiceTranscripts.Add($"Question {e.QuestionId}: {e.Transcript}");
        }

        private int GetSpeechToTextLanguageCode()
        {
            return _mainWindow.CurrentRequest.Language.Equals("English", StringComparison.OrdinalIgnoreCase)
                ? 1
                : 0;
        }

        private string GetSelectedSeverity()
        {
            RadioButton? selected = FindVisualChildren<RadioButton>(this)
                .FirstOrDefault(radioButton => radioButton.GroupName == "Severity" && radioButton.IsChecked == true);

            return selected?.Tag?.ToString() ?? "";
        }

        private void SelectSeverity(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return;
            }

            foreach (RadioButton radioButton in FindVisualChildren<RadioButton>(this))
            {
                string tagValue = radioButton.Tag?.ToString() ?? "";
                string contentValue = ReadTextBlockContent(radioButton);

                if (tagValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || contentValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || tagValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || value.Contains(tagValue, StringComparison.OrdinalIgnoreCase)
                    || contentValue.Contains(value, StringComparison.OrdinalIgnoreCase))
                {
                    radioButton.IsChecked = true;
                    return;
                }
            }
        }

        private static string MapSeverityResponse(string value)
        {
            return value.Trim() switch
            {
                "1" => "Mild",
                "2" => "Low",
                "3" => "Moderate",
                "4" => "High",
                "5" => "Severe",
                _ => value
            };
        }

        private static string ReadTextBlockContent(DependencyObject parent)
        {
            TextBlock? textBlock = FindVisualChildren<TextBlock>(parent).FirstOrDefault();
            return textBlock?.Text ?? "";
        }

        private static IEnumerable<T> FindVisualChildren<T>(DependencyObject parent)
            where T : DependencyObject
        {
            if (parent == null)
            {
                yield break;
            }

            for (int i = 0; i < VisualTreeHelper.GetChildrenCount(parent); i++)
            {
                DependencyObject child = VisualTreeHelper.GetChild(parent, i);

                if (child is T typedChild)
                {
                    yield return typedChild;
                }

                foreach (T childOfChild in FindVisualChildren<T>(child))
                {
                    yield return childOfChild;
                }
            }
        }
    }
}
