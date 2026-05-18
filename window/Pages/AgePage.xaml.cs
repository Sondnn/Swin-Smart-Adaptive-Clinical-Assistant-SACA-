using System;
using System.Windows;
using System.Windows.Controls;
using SACA.WindowsApp.Services;

namespace SACA.WindowsApp.Pages
{
    /// <summary>
    /// Interaction logic for AgePage.xaml
    /// </summary>
    public partial class AgePage : UserControl
    {
        private readonly MainWindow _mainWindow;
        private string _recordedAge = "";

        public AgePage(MainWindow mainWindow)
        {
            InitializeComponent();
            _mainWindow = mainWindow;
            AgeVoiceRecorder.Configure(GetSpeechToTextLanguageCode);
            AgeVoiceRecorder.TranscriptReceived += VoiceRecorder_TranscriptReceived;

            if (!string.IsNullOrWhiteSpace(_mainWindow.CurrentRequest.AgeGroup))
            {
                SelectRadioValue(_mainWindow.CurrentRequest.AgeGroup);
            }
        }

        private void Back_Click(object sender, RoutedEventArgs e)
        {
            _mainWindow.NavigateToPatientInfo();
        }

        private void Continue_Click(object sender, RoutedEventArgs e)
        {
            string age = GetSelectedValue();

            if (string.IsNullOrWhiteSpace(age))
            {
                age = _recordedAge;
            }

            if (string.IsNullOrWhiteSpace(age))
            {
                MessageBox.Show("Please select age group, or answer using voice.");
                return;
            }

            _mainWindow.CurrentRequest.AgeGroup = age;
            _mainWindow.NavigateToSymptoms();
        }

        private void VoiceRecorder_TranscriptReceived(object? sender, Controls.VoiceTranscribedEventArgs e)
        {
            _recordedAge = ParsedResponseReader.ReadSingleValue(e.ParsedResponseJson);
            SelectRadioValue(_recordedAge);
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

        private string GetSelectedValue()
        {
            if (YoungerRadioButton.IsChecked == true)
            {
                return YoungerRadioButton.Tag?.ToString() ?? "";
            }

            if (OlderRadioButton.IsChecked == true)
            {
                return OlderRadioButton.Tag?.ToString() ?? "";
            }

            return "";
        }

        private void SelectRadioValue(string value)
        {
            YoungerRadioButton.IsChecked = value.Contains("younger", StringComparison.OrdinalIgnoreCase)
                || value.Contains("65 years old or younger", StringComparison.OrdinalIgnoreCase)
                || value.Trim() == "0";
            OlderRadioButton.IsChecked = value.Contains("older", StringComparison.OrdinalIgnoreCase)
                || value.Contains("older than 65", StringComparison.OrdinalIgnoreCase)
                || value.Trim() == "1";
        }
    }
}
