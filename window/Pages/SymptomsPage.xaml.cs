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
    /// Interaction logic for SymptomsPage.xaml
    /// </summary>
    public partial class SymptomsPage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private string _recordedSymptomsDescription = "";
        private List<string> _recordedSymptoms = new();

        public SymptomsPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            SymptomsVoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            SymptomsVoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;

            if (_mainWindow.CurrentRequest.Symptoms.Any())
            {
                SelectCheckBoxes(_mainWindow.CurrentRequest.Symptoms);
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToAge();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            var symptoms = GetSelectedSymptoms();

            if (!symptoms.Any())
            {
                symptoms = _recordedSymptoms;
            }

            if (!symptoms.Any())
            {
                MessageBox.Show("Please select at least one symptom, or answer using voice.");
                return;
            }

            _mainWindow.CurrentRequest.Symptoms = symptoms;
            _mainWindow.CurrentRequest.Description = _recordedSymptomsDescription;
            _mainWindow.CurrentRequest.AudioRecordingPath = SymptomsVoiceRecorder.LastRecordingPath;

            _mainWindow.NavigateToSeverity();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            if (e.QuestionId == 3)
            {
                _recordedSymptoms = ParsedResponseReader.ReadStringList(e.ParsedResponseJson);
                _recordedSymptomsDescription = e.Transcript;
                SelectCheckBoxes(_recordedSymptoms);
                TranscriptTextBlock.Text = e.Transcript;
                TranscriptBorder.Visibility = Visibility.Visible;
            }
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

        private List<string> GetSelectedSymptoms()
        {
            var symptoms = new List<string>();

            foreach (var checkBox in FindVisualChildren<CheckBox>(this))
            {
                if (checkBox.IsChecked == true && checkBox.Content != null)
                {
                    symptoms.Add(checkBox.Tag?.ToString() ?? checkBox.Content.ToString() ?? "");
                }
            }

            return symptoms;
        }

        private void SelectCheckBoxes(IEnumerable<string> values)
        {
            foreach (CheckBox checkBox in FindVisualChildren<CheckBox>(this))
            {
                string checkBoxValue = checkBox.Content?.ToString() ?? "";
                string tagValue = checkBox.Tag?.ToString() ?? "";
                string normalisedCheckBoxValue = NormaliseSelectionValue(checkBoxValue);
                string normalisedTagValue = NormaliseSelectionValue(tagValue);
                checkBox.IsChecked = values.Any(value =>
                {
                    string normalisedValue = NormaliseSelectionValue(value);

                    return normalisedCheckBoxValue.Equals(normalisedValue, StringComparison.OrdinalIgnoreCase)
                    || normalisedTagValue.Equals(normalisedValue, StringComparison.OrdinalIgnoreCase)
                    || checkBoxValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || tagValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || checkBoxValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || tagValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || value.Contains(checkBoxValue, StringComparison.OrdinalIgnoreCase);
                });
            }
        }

        private static string NormaliseSelectionValue(string value)
        {
            return value.Trim()
                .ToLowerInvariant()
                .Replace("-", "_")
                .Replace("/", "_")
                .Replace(" ", "_");
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
