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
        private string _recordedSeverity = "";

        public SymptomsPage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            SymptomsVoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            SeverityVoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            SymptomsVoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
            SeverityVoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToPatientInfo();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            var symptoms = GetSelectedSymptoms();
            string severity = GetComboBoxValue(SeverityComboBox);

            if (!symptoms.Any())
            {
                symptoms = _recordedSymptoms;
            }

            if (string.IsNullOrWhiteSpace(severity))
            {
                severity = _recordedSeverity;
            }

            if (!symptoms.Any() || string.IsNullOrWhiteSpace(severity))
            {
                MessageBox.Show("Please select at least one symptom and severity level, or answer them using voice.");
                return;
            }

            _mainWindow.CurrentRequest.Symptoms = symptoms;
            _mainWindow.CurrentRequest.Severity = severity;
            _mainWindow.CurrentRequest.Description = _recordedSymptomsDescription;
            _mainWindow.CurrentRequest.AudioRecordingPath = !string.IsNullOrWhiteSpace(SeverityVoiceRecorder.LastRecordingPath)
                ? SeverityVoiceRecorder.LastRecordingPath
                : SymptomsVoiceRecorder.LastRecordingPath;

            _mainWindow.NavigateToDuration();
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
            else if (e.QuestionId == 5)
            {
                _recordedSeverity = ParsedResponseReader.ReadSingleValue(e.ParsedResponseJson);
                SelectComboBoxValue(SeverityComboBox, _recordedSeverity);
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
                    symptoms.Add(checkBox.Content.ToString() ?? "");
                }
            }

            return symptoms;
        }

        private string GetComboBoxValue(ComboBox comboBox)
        {
            if (comboBox.SelectedItem is ComboBoxItem item)
            {
                return item.Content?.ToString() ?? "";
            }

            return "";
        }

        private void SelectCheckBoxes(IEnumerable<string> values)
        {
            foreach (CheckBox checkBox in FindVisualChildren<CheckBox>(this))
            {
                string checkBoxValue = checkBox.Content?.ToString() ?? "";
                checkBox.IsChecked = values.Any(value =>
                    checkBoxValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || checkBoxValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || value.Contains(checkBoxValue, StringComparison.OrdinalIgnoreCase));
            }
        }

        private static void SelectComboBoxValue(ComboBox comboBox, string value)
        {
            foreach (ComboBoxItem item in comboBox.Items)
            {
                string itemValue = item.Content?.ToString() ?? "";

                if (itemValue.Equals(value, StringComparison.OrdinalIgnoreCase)
                    || itemValue.Contains(value, StringComparison.OrdinalIgnoreCase)
                    || value.Contains(itemValue, StringComparison.OrdinalIgnoreCase))
                {
                    comboBox.SelectedItem = item;
                    return;
                }
            }
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
